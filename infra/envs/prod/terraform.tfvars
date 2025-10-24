# Terraform variables for SWEN AIOps production environment
# This file is managed by the AI engine for GitOps automation

# Provider regions
aws_region     = "us-east-1"
alibaba_region = "ap-southeast-1"

# Cluster configurations
aws_node_count        = 2
alibaba_node_count    = 2
aws_instance_type     = "t3.medium"
alibaba_instance_type = "t3.medium"

# Service 1 - AI-managed placement
service1_provider = "aws"
service1_region   = "us-east-1"
service1_instance = "t3.medium"

# Service 2 - AI-managed placement
service2_provider = "aws"
service2_region   = "us-east-1"
service2_instance = "t3.medium"

# Service 3 - AI-managed placement
service3_provider = "aws"
service3_region   = "ap-southeast-1"
service3_instance = "t3.medium"
