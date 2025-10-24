# Main Terraform configuration for SWEN AIOps production environment

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration for state management
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Primary AWS provider (simulating AWS)
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "production"
      Project     = "swen-aiops"
      ManagedBy   = "terraform"
    }
  }
}

# Secondary AWS provider (simulating Alibaba Cloud)
provider "aws" {
  alias  = "alibaba_sim"
  region = var.alibaba_region

  default_tags {
    tags = {
      Environment = "production"
      Project     = "swen-aiops"
      Provider    = "alibaba-simulated"
      ManagedBy   = "terraform"
    }
  }
}

# AWS Cluster
module "cluster_aws" {
  source = "../../modules/cluster"

  providers = {
    aws = aws
  }

  name          = "swen-aws"
  node_count    = var.aws_node_count
  instance_type = var.aws_instance_type
  region        = var.aws_region

  tags = {
    Provider = "aws"
    Cluster  = "primary"
  }
}

# Alibaba Cluster (simulated with AWS)
module "cluster_alibaba" {
  source = "../../modules/cluster"

  providers = {
    aws = aws.alibaba_sim
  }

  name          = "swen-alibaba"
  node_count    = var.alibaba_node_count
  instance_type = var.alibaba_instance_type
  region        = var.alibaba_region

  tags = {
    Provider = "alibaba"
    Cluster  = "secondary"
  }
}

# Service 1 - AI-routed deployment
module "service1_aws" {
  source = "../../modules/app"
  count  = var.service1_provider == "aws" ? 1 : 0

  providers = {
    aws = aws
  }

  name              = "service1"
  instance_type     = var.service1_instance
  vpc_id            = module.cluster_aws.vpc_id
  subnet_id         = module.cluster_aws.subnet_id
  security_group_id = module.cluster_aws.security_group_id
  provider_name     = "aws"

  tags = {
    Service    = "service1"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}

module "service1_alibaba" {
  source = "../../modules/app"
  count  = var.service1_provider == "alibaba" ? 1 : 0

  providers = {
    aws = aws.alibaba_sim
  }

  name              = "service1"
  instance_type     = var.service1_instance
  vpc_id            = module.cluster_alibaba.vpc_id
  subnet_id         = module.cluster_alibaba.subnet_id
  security_group_id = module.cluster_alibaba.security_group_id
  provider_name     = "alibaba"

  tags = {
    Service    = "service1"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}

# Service 2 - AI-routed deployment
module "service2_aws" {
  source = "../../modules/app"
  count  = var.service2_provider == "aws" ? 1 : 0

  providers = {
    aws = aws
  }

  name              = "service2"
  instance_type     = var.service2_instance
  vpc_id            = module.cluster_aws.vpc_id
  subnet_id         = module.cluster_aws.subnet_id
  security_group_id = module.cluster_aws.security_group_id
  provider_name     = "aws"

  tags = {
    Service    = "service2"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}

module "service2_alibaba" {
  source = "../../modules/app"
  count  = var.service2_provider == "alibaba" ? 1 : 0

  providers = {
    aws = aws.alibaba_sim
  }

  name              = "service2"
  instance_type     = var.service2_instance
  vpc_id            = module.cluster_alibaba.vpc_id
  subnet_id         = module.cluster_alibaba.subnet_id
  security_group_id = module.cluster_alibaba.security_group_id
  provider_name     = "alibaba"

  tags = {
    Service    = "service2"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}

# Service 3 - AI-routed deployment
module "service3_aws" {
  source = "../../modules/app"
  count  = var.service3_provider == "aws" ? 1 : 0

  providers = {
    aws = aws
  }

  name              = "service3"
  instance_type     = var.service3_instance
  vpc_id            = module.cluster_aws.vpc_id
  subnet_id         = module.cluster_aws.subnet_id
  security_group_id = module.cluster_aws.security_group_id
  provider_name     = "aws"

  tags = {
    Service    = "service3"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}

module "service3_alibaba" {
  source = "../../modules/app"
  count  = var.service3_provider == "alibaba" ? 1 : 0

  providers = {
    aws = aws.alibaba_sim
  }

  name              = "service3"
  instance_type     = var.service3_instance
  vpc_id            = module.cluster_alibaba.vpc_id
  subnet_id         = module.cluster_alibaba.subnet_id
  security_group_id = module.cluster_alibaba.security_group_id
  provider_name     = "alibaba"

  tags = {
    Service    = "service3"
    AIManaged  = "true"
    CostCenter = "engineering"
  }
}
