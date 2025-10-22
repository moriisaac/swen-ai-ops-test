# SWEN AIOps Infrastructure

This directory contains the Infrastructure as Code (IaC) for the SWEN AIOps platform.

## Structure

```
infra/
├── modules/
│   ├── cluster/    # Kubernetes cluster module
│   └── app/        # Application deployment module
└── envs/
    └── prod/       # Production environment
```

## Modules

### Cluster Module
Creates a cloud infrastructure foundation including:
- VPC and networking
- Security groups
- Compute resources for Kubernetes nodes

### App Module
Deploys application services with:
- EC2 instances
- Monitoring integration
- CloudWatch alarms

## Usage

### Initialize Terraform

```bash
cd envs/prod
terraform init
```

### Plan Changes

```bash
terraform plan
```

### Apply Changes

```bash
terraform apply
```

### View Outputs

```bash
terraform output
```

## AI-Managed Variables

The following variables are automatically managed by the AI engine:

- `service1_provider` - Cloud provider for service 1
- `service2_provider` - Cloud provider for service 2
- `service3_provider` - Cloud provider for service 3
- `service*_instance` - Instance types for each service

These variables are updated via GitOps when the AI engine determines a better placement.

## Multi-Cloud Setup

This infrastructure simulates a multi-cloud environment:
- **AWS Provider**: Primary cloud provider
- **Alibaba Provider**: Simulated using a second AWS provider with different region

In production, you would configure actual Alibaba Cloud credentials.

## State Management

Terraform state is stored locally by default. For production use, configure remote state:

```hcl
backend "s3" {
  bucket = "swen-terraform-state"
  key    = "prod/terraform.tfstate"
  region = "us-east-1"
}
```

## Security Considerations

- Store sensitive variables in environment variables or secret management systems
- Use IAM roles with least privilege
- Enable encryption for state files
- Implement state locking for team environments
