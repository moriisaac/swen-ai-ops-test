#!/bin/bash
"""
Local GitOps Deployment Script
Simulates the GitLab CI/CD pipeline for local development and testing
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TF_ROOT="./infra/envs/prod"
TF_VERSION="1.5.0"
PROJECT_ROOT="$(pwd)"

echo -e "${BLUE}🚀 SWEN AIOps - Local GitOps Deployment${NC}"
echo "================================================"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if we're in a Git repository
check_git_repo() {
    if [ ! -d ".git" ]; then
        print_error "Not in a Git repository. Please run from project root."
        exit 1
    fi
    print_status "Git repository detected"
}

# Function to validate Terraform configuration
validate_terraform() {
    echo -e "\n${BLUE}📋 Stage 1: Terraform Validation${NC}"
    echo "----------------------------------------"
    
    if [ ! -d "$TF_ROOT" ]; then
        print_error "Terraform directory not found: $TF_ROOT"
        exit 1
    fi
    
    cd "$TF_ROOT"
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_warning "Terraform not found. Using Docker..."
        TF_CMD="docker run --rm -v $(pwd):/workspace -w /workspace hashicorp/terraform:$TF_VERSION"
    else
        TF_CMD="terraform"
        print_status "Using local Terraform installation"
    fi
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    $TF_CMD init -backend=false
    
    # Validate configuration
    print_status "Validating Terraform configuration..."
    $TF_CMD validate
    
    # Format check
    print_status "Checking Terraform formatting..."
    $TF_CMD fmt -check -recursive || {
        print_warning "Terraform formatting issues found. Running fmt..."
        $TF_CMD fmt -recursive
    }
    
    print_status "Terraform validation completed"
    cd "$PROJECT_ROOT"
}

# Function to run policy check
run_policy_check() {
    echo -e "\n${BLUE}⚖️  Stage 2: Policy Evaluation${NC}"
    echo "----------------------------------------"
    
    # Check if this is an AI recommendation branch
    CURRENT_BRANCH=$(git branch --show-current)
    
    if [[ "$CURRENT_BRANCH" =~ ^ai-recommendation/.* ]]; then
        print_status "AI recommendation branch detected: $CURRENT_BRANCH"
        
        # Check for metadata file
        METADATA_FILE="$TF_ROOT/ai-metadata.json"
        if [ -f "$METADATA_FILE" ]; then
            print_status "Found AI metadata file"
            
            # Run policy gate
            print_status "Running policy evaluation..."
            python3 ops/policy_gate.py
            POLICY_EXIT_CODE=$?
            
            if [ $POLICY_EXIT_CODE -eq 0 ]; then
                print_status "AUTO-APPROVE: Change meets policy criteria"
                AUTO_APPROVE=true
            else
                print_warning "MANUAL-APPROVAL: Change requires human review"
                AUTO_APPROVE=false
            fi
        else
            print_warning "No metadata found, defaulting to manual approval"
            AUTO_APPROVE=false
        fi
    else
        print_status "Regular branch: $CURRENT_BRANCH"
        AUTO_APPROVE=false
    fi
    
    echo "AUTO_APPROVE=$AUTO_APPROVE"
}

# Function to run Terraform plan
run_terraform_plan() {
    echo -e "\n${BLUE}📊 Stage 3: Terraform Plan${NC}"
    echo "----------------------------------------"
    
    cd "$TF_ROOT"
    
    # Initialize with backend (if configured)
    print_status "Initializing Terraform with backend..."
    $TF_CMD init
    
    # Create plan
    print_status "Creating Terraform plan..."
    $TF_CMD plan -out=tfplan
    
    # Show plan summary
    print_status "Terraform plan summary:"
    $TF_CMD show tfplan
    
    # Save plan as JSON
    print_status "Saving plan as JSON..."
    $TF_CMD show -json tfplan > plan.json
    
    print_status "Terraform plan completed"
    cd "$PROJECT_ROOT"
}

# Function to apply Terraform changes
apply_terraform() {
    echo -e "\n${BLUE}🚀 Stage 4: Terraform Apply${NC}"
    echo "----------------------------------------"
    
    cd "$TF_ROOT"
    
    if [ "$AUTO_APPROVE" == "true" ]; then
        print_status "Auto-applying approved AI recommendation..."
        $TF_CMD apply -auto-approve tfplan
    else
        print_warning "Manual approval required"
        echo "Do you want to apply the Terraform plan? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Applying Terraform plan..."
            $TF_CMD apply tfplan
        else
            print_warning "Terraform apply cancelled"
            cd "$PROJECT_ROOT"
            return 1
        fi
    fi
    
    # Save outputs
    print_status "Saving Terraform outputs..."
    $TF_CMD output -json > outputs.json
    
    print_status "Terraform apply completed"
    cd "$PROJECT_ROOT"
}

# Function to notify dashboard
notify_dashboard() {
    echo -e "\n${BLUE}📢 Stage 5: Dashboard Notification${NC}"
    echo "----------------------------------------"
    
    CURRENT_BRANCH=$(git branch --show-current)
    COMMIT_SHA=$(git rev-parse HEAD)
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    print_status "Deployment completed for branch: $CURRENT_BRANCH"
    print_status "Commit: $COMMIT_SHA"
    
    # Send notification to dashboard API (if running)
    DASHBOARD_URL="http://localhost:8001"
    if curl -s -o /dev/null -w "%{http_code}" "$DASHBOARD_URL/healthz" | grep -q "200"; then
        print_status "Sending notification to dashboard..."
        
        curl -X POST "$DASHBOARD_URL/api/deployments" \
          -H "Content-Type: application/json" \
          -d "{
            \"branch\": \"$CURRENT_BRANCH\",
            \"commit\": \"$COMMIT_SHA\",
            \"status\": \"success\",
            \"timestamp\": \"$TIMESTAMP\",
            \"auto_approved\": $AUTO_APPROVE
          }" || print_warning "Failed to notify dashboard"
    else
        print_warning "Dashboard API not available for notification"
    fi
}

# Function to show deployment summary
show_summary() {
    echo -e "\n${GREEN}🎉 Deployment Summary${NC}"
    echo "===================="
    echo "Branch: $(git branch --show-current)"
    echo "Commit: $(git rev-parse --short HEAD)"
    echo "Auto-approved: $AUTO_APPROVE"
    echo "Timestamp: $(date)"
    echo ""
    echo "Next steps:"
    echo "- Check dashboard at http://localhost:8501"
    echo "- Monitor metrics at http://localhost:3000 (Grafana)"
    echo "- View API status at http://localhost:8001/healthz"
}

# Main execution
main() {
    echo "Starting GitOps deployment pipeline..."
    echo ""
    
    # Check prerequisites
    check_git_repo
    
    # Run pipeline stages
    validate_terraform
    run_policy_check
    run_terraform_plan
    
    # Ask for confirmation before apply
    echo ""
    echo -e "${YELLOW}Ready to apply changes. Continue? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled by user"
        exit 0
    fi
    
    apply_terraform
    notify_dashboard
    show_summary
    
    print_status "GitOps deployment pipeline completed successfully!"
}

# Handle command line arguments
case "${1:-}" in
    "validate")
        check_git_repo
        validate_terraform
        ;;
    "plan")
        check_git_repo
        validate_terraform
        run_policy_check
        run_terraform_plan
        ;;
    "apply")
        check_git_repo
        validate_terraform
        run_policy_check
        run_terraform_plan
        apply_terraform
        notify_dashboard
        ;;
    "policy")
        run_policy_check
        ;;
    *)
        main
        ;;
esac


