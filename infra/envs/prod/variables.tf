# Variables for SWEN AIOps production environment

# Provider configurations
variable "aws_region" {
  description = "AWS region for primary cluster"
  type        = string
  default     = "us-east-1"
}

variable "alibaba_region" {
  description = "Region for Alibaba cluster (simulated with AWS)"
  type        = string
  default     = "ap-southeast-1"
}

# Cluster configurations
variable "aws_node_count" {
  description = "Number of nodes in AWS cluster"
  type        = number
  default     = 2
}

variable "alibaba_node_count" {
  description = "Number of nodes in Alibaba cluster"
  type        = number
  default     = 2
}

variable "aws_instance_type" {
  description = "Instance type for AWS cluster nodes"
  type        = string
  default     = "t3.medium"
}

variable "alibaba_instance_type" {
  description = "Instance type for Alibaba cluster nodes"
  type        = string
  default     = "t3.medium"
}

# Service 1 configuration (AI-managed)
variable "service1_provider" {
  description = "Cloud provider for service1 (aws or alibaba)"
  type        = string
  default     = "aws"
  
  validation {
    condition     = contains(["aws", "alibaba"], var.service1_provider)
    error_message = "Provider must be either 'aws' or 'alibaba'."
  }
}

variable "service1_region" {
  description = "Region for service1"
  type        = string
  default     = "us-east-1"
}

variable "service1_instance" {
  description = "Instance type for service1"
  type        = string
  default     = "t3.medium"
}

# Service 2 configuration (AI-managed)
variable "service2_provider" {
  description = "Cloud provider for service2 (aws or alibaba)"
  type        = string
  default     = "aws"
  
  validation {
    condition     = contains(["aws", "alibaba"], var.service2_provider)
    error_message = "Provider must be either 'aws' or 'alibaba'."
  }
}

variable "service2_region" {
  description = "Region for service2"
  type        = string
  default     = "us-east-1"
}

variable "service2_instance" {
  description = "Instance type for service2"
  type        = string
  default     = "t3.medium"
}

# Service 3 configuration (AI-managed)
variable "service3_provider" {
  description = "Cloud provider for service3 (aws or alibaba)"
  type        = string
  default     = "alibaba"
  
  validation {
    condition     = contains(["aws", "alibaba"], var.service3_provider)
    error_message = "Provider must be either 'aws' or 'alibaba'."
  }
}

variable "service3_region" {
  description = "Region for service3"
  type        = string
  default     = "ap-southeast-1"
}

variable "service3_instance" {
  description = "Instance type for service3"
  type        = string
  default     = "t3.medium"
}
