# Outputs for SWEN AIOps production environment

# Cluster outputs
output "aws_cluster_name" {
  description = "AWS cluster name"
  value       = module.cluster_aws.cluster_name
}

output "alibaba_cluster_name" {
  description = "Alibaba cluster name"
  value       = module.cluster_alibaba.cluster_name
}

output "aws_vpc_id" {
  description = "AWS VPC ID"
  value       = module.cluster_aws.vpc_id
}

output "alibaba_vpc_id" {
  description = "Alibaba VPC ID"
  value       = module.cluster_alibaba.vpc_id
}

# Service outputs
output "service1_instance_id" {
  description = "Service 1 instance ID"
  value       = module.service1.instance_id
}

output "service1_public_ip" {
  description = "Service 1 public IP"
  value       = module.service1.public_ip
}

output "service1_provider" {
  description = "Service 1 current provider"
  value       = var.service1_provider
}

output "service2_instance_id" {
  description = "Service 2 instance ID"
  value       = module.service2.instance_id
}

output "service2_public_ip" {
  description = "Service 2 public IP"
  value       = module.service2.public_ip
}

output "service2_provider" {
  description = "Service 2 current provider"
  value       = var.service2_provider
}

output "service3_instance_id" {
  description = "Service 3 instance ID"
  value       = module.service3.instance_id
}

output "service3_public_ip" {
  description = "Service 3 public IP"
  value       = module.service3.public_ip
}

output "service3_provider" {
  description = "Service 3 current provider"
  value       = var.service3_provider
}

# Summary output
output "deployment_summary" {
  description = "Summary of current deployment"
  value = {
    aws_cluster = {
      name       = module.cluster_aws.cluster_name
      vpc_id     = module.cluster_aws.vpc_id
      node_count = var.aws_node_count
    }
    alibaba_cluster = {
      name       = module.cluster_alibaba.cluster_name
      vpc_id     = module.cluster_alibaba.vpc_id
      node_count = var.alibaba_node_count
    }
    services = {
      service1 = {
        provider   = var.service1_provider
        public_ip  = module.service1.public_ip
      }
      service2 = {
        provider   = var.service2_provider
        public_ip  = module.service2.public_ip
      }
      service3 = {
        provider   = var.service3_provider
        public_ip  = module.service3.public_ip
      }
    }
  }
}
