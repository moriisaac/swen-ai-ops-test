# App Module - Deploys application services with monitoring

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "name" {
  description = "Application name"
  type        = string
}

variable "instance_type" {
  description = "Instance type for the application"
  type        = string
  default     = "t3.medium"
}

variable "vpc_id" {
  description = "VPC ID where the app will be deployed"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the app"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID"
  type        = string
}

variable "provider_name" {
  description = "Cloud provider name (aws or alibaba)"
  type        = string
  default     = "aws"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# IAM role for EC2 instance
resource "aws_iam_role" "app" {
  name = "${var.name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_instance_profile" "app" {
  name = "${var.name}-profile"
  role = aws_iam_role.app.name
}

# EC2 Instance for the application
resource "aws_instance" "app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.app.name

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              service docker start
              usermod -a -G docker ec2-user
              
              # Install Prometheus node exporter
              wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
              tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
              cd node_exporter-1.6.1.linux-amd64
              nohup ./node_exporter &
              
              # Create a simple app
              docker run -d -p 80:80 --name ${var.name} nginx:latest
              EOF

  tags = merge(
    var.tags,
    {
      Name     = var.name
      Provider = var.provider_name
    }
  )
}

# CloudWatch alarms for monitoring
resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.name}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  tags = var.tags
}

# Outputs
output "instance_id" {
  description = "Instance ID"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_instance.app.public_ip
}

output "private_ip" {
  description = "Private IP address"
  value       = aws_instance.app.private_ip
}
