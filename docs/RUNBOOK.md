# SWEN AIOps Platform Runbook

## Quick Start Guide

This runbook provides step-by-step instructions for deploying, operating, and troubleshooting the SWEN AIOps platform.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running the Platform](#running-the-platform)
4. [Monitoring & Operations](#monitoring--operations)
5. [Troubleshooting](#troubleshooting)
6. [Common Tasks](#common-tasks)
7. [Emergency Procedures](#emergency-procedures)

---

## Prerequisites

### Required Software

```bash
# Core tools
terraform >= 1.0
python >= 3.8
git >= 2.30
docker >= 20.10 (optional, for local testing)

# Python packages
pip install -r ai-engine/requirements.txt
pip install -r dashboard/api/requirements.txt
pip install -r dashboard/ui/requirements.txt
```

### Cloud Provider Credentials

**AWS:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Alibaba Cloud (if using real Alibaba):**
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-secret-key"
export ALIBABA_CLOUD_REGION="ap-southeast-1"
```

### GitLab Configuration (for CI/CD)

```bash
export GITLAB_URL="https://gitlab.com"
export GITLAB_TOKEN="your-personal-access-token"
export CI_PROJECT_ID="your-project-id"
```

---

## Initial Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/moriisaac/swen-aio-test.git
cd swen-aio-test
```

### Step 2: Initialize Terraform

```bash
cd infra/envs/prod
terraform init
terraform validate
```

### Step 3: Review and Customize Variables

Edit `terraform.tfvars`:
```hcl
# Adjust regions and instance types as needed
aws_region = "us-east-1"
alibaba_region = "ap-southeast-1"

# Service placement (will be managed by AI later)
service1_provider = "aws"
service2_provider = "aws"
service3_provider = "alibaba"
```

### Step 4: Deploy Infrastructure

```bash
# Plan
terraform plan -out=tfplan

# Review the plan carefully
terraform show tfplan

# Apply
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

### Step 5: Set Up Python Environment

```bash
cd ../../../

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ai-engine/requirements.txt
pip install -r dashboard/api/requirements.txt
pip install -r dashboard/ui/requirements.txt
```

---

## Running the Platform

### Start All Components

Use this script to start all services:

```bash
#!/bin/bash
# start-all.sh

# Start telemetry simulator
cd ai-engine
python simulator.py &
SIMULATOR_PID=$!
echo "Simulator started (PID: $SIMULATOR_PID)"

# Start AI engine
python engine.py &
ENGINE_PID=$!
echo "AI Engine started (PID: $ENGINE_PID)"

# Start dashboard API
cd ../dashboard/api
python main.py &
API_PID=$!
echo "Dashboard API started (PID: $API_PID)"

# Start dashboard UI
cd ../ui
streamlit run app.py &
UI_PID=$!
echo "Dashboard UI started (PID: $UI_PID)"

echo ""
echo "All services started!"
echo "Dashboard: http://localhost:8501"
echo "API: http://localhost:8000"
echo ""
echo "To stop all services:"
echo "kill $SIMULATOR_PID $ENGINE_PID $API_PID $UI_PID"
```

Make it executable and run:
```bash
chmod +x start-all.sh
./start-all.sh
```

### Start Individual Components

**Telemetry Simulator:**
```bash
cd ai-engine
python simulator.py --interval 5
```

**AI Engine:**
```bash
cd ai-engine
python engine.py
```

**Dashboard API:**
```bash
cd dashboard/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Dashboard UI:**
```bash
cd dashboard/ui
streamlit run app.py --server.port 8501
```

### Access Points

- **Dashboard UI:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/healthz
- **Prometheus Metrics:** http://localhost:8000/metrics

---

## Monitoring & Operations

### Health Checks

**Check API Health:**
```bash
curl http://localhost:8000/healthz | jq
```

Expected response:
```json
{
  "status": "ok",
  "active_providers": ["aws", "alibaba"],
  "last_ai_commit": "ai-recommendation/service1/...",
  "services": {
    "service1": "aws",
    "service2": "aws",
    "service3": "alibaba"
  },
  "timestamp": "2025-10-22T20:00:00Z"
}
```

**Check Telemetry:**
```bash
curl http://localhost:8000/api/telemetry | jq
```

**Check AI Decisions:**
```bash
curl http://localhost:8000/api/decisions | jq '.decisions[-5:]'
```

### Log Locations

```bash
# AI Engine logs
tail -f ai-engine/ai_engine.log

# Simulator logs (stdout)
# API logs (stdout via uvicorn)
# Dashboard logs (stdout via streamlit)
```

### Metrics Collection

**Prometheus Scraping:**
```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'swen-dashboard'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**View Metrics:**
```bash
curl http://localhost:8000/metrics
```

---

## Troubleshooting

### Issue: AI Engine Not Making Decisions

**Symptoms:**
- No new entries in `ai_decisions.json`
- No Git branches being created

**Diagnosis:**
```bash
# Check if engine is running
ps aux | grep engine.py

# Check logs
tail -f ai-engine/ai_engine.log

# Check telemetry file exists
ls -la ai-engine/latest_telemetry.json
```

**Solutions:**
1. Ensure simulator is running and generating telemetry
2. Check Git repository is initialized
3. Verify confidence threshold (default 0.7)
4. Check for errors in logs

### Issue: Dashboard Not Showing Data

**Symptoms:**
- Empty dashboard
- "Unable to fetch data" errors

**Diagnosis:**
```bash
# Check API is running
curl http://localhost:8000/healthz

# Check file paths
ls -la ai-engine/latest_telemetry.json
ls -la ai-engine/ai_decisions.json
```

**Solutions:**
1. Verify API URL in dashboard sidebar
2. Check API is running on correct port
3. Ensure telemetry files exist and are readable
4. Check browser console for errors

### Issue: Terraform Apply Fails

**Symptoms:**
- Terraform apply errors
- Resource creation failures

**Diagnosis:**
```bash
# Check credentials
aws sts get-caller-identity

# Validate configuration
terraform validate

# Check state
terraform state list
```

**Solutions:**
1. Verify AWS credentials are set
2. Check for resource naming conflicts
3. Review error messages carefully
4. Check AWS service limits

### Issue: GitLab CI Pipeline Failing

**Symptoms:**
- Pipeline jobs failing
- Terraform errors in CI

**Diagnosis:**
```bash
# Check CI variables are set
# In GitLab: Settings > CI/CD > Variables

# Validate locally
terraform init
terraform validate
```

**Solutions:**
1. Ensure CI/CD variables are configured
2. Check Terraform backend is accessible
3. Verify GitLab runner has necessary permissions
4. Review pipeline logs in GitLab

### Issue: High Memory Usage

**Symptoms:**
- System slowdown
- Out of memory errors

**Diagnosis:**
```bash
# Check memory usage
ps aux --sort=-%mem | head -10

# Check for memory leaks
top -o %MEM
```

**Solutions:**
1. Restart services
2. Reduce telemetry update frequency
3. Limit decision history size
4. Check for infinite loops in code

---

## Common Tasks

### Task: Manually Trigger AI Decision

```bash
cd ai-engine

# Generate sample telemetry with specific conditions
python simulator.py --sample --output latest_telemetry.json

# Edit telemetry to force a decision
# (e.g., make AWS very expensive)

# Run engine once
python -c "
from engine import CostOptimizationEngine
engine = CostOptimizationEngine()
telemetry = engine._read_telemetry()
for service, metrics in telemetry.items():
    provider, decision = engine.make_decision(service, metrics)
    if provider:
        print(f'{service}: {decision}')
"
```

### Task: Reset to Clean State

```bash
# Stop all services
pkill -f "python.*simulator.py"
pkill -f "python.*engine.py"
pkill -f "uvicorn"
pkill -f "streamlit"

# Clear decision history
rm -f ai-engine/ai_decisions.json
echo "[]" > ai-engine/ai_decisions.json

# Reset telemetry
rm -f ai-engine/latest_telemetry.json

# Destroy infrastructure (if needed)
cd infra/envs/prod
terraform destroy -auto-approve
```

### Task: Update Service Placement

```bash
cd infra/envs/prod

# Edit terraform.tfvars
vim terraform.tfvars

# Change provider
# service1_provider = "alibaba"  # was "aws"

# Apply changes
terraform plan
terraform apply
```

### Task: View Cost Analysis

```bash
# Via API
curl http://localhost:8000/api/cost-analysis | jq

# Via Dashboard
# Navigate to "Cost Analysis" tab in UI

# Via Terraform outputs
cd infra/envs/prod
terraform output deployment_summary
```

### Task: Export Metrics for Analysis

```bash
# Export telemetry history
curl http://localhost:8000/api/telemetry > telemetry_$(date +%Y%m%d).json

# Export decisions
curl http://localhost:8000/api/decisions > decisions_$(date +%Y%m%d).json

# Export metrics
curl http://localhost:8000/api/metrics > metrics_$(date +%Y%m%d).json
```

### Task: Simulate Provider Outage

```bash
# Edit simulator to set high latency for AWS
cd ai-engine

python -c "
import json
data = json.load(open('latest_telemetry.json'))
for service in data:
    if 'aws' in data[service]:
        data[service]['aws']['latency'] = 9999
        data[service]['aws']['available_gpus'] = 0
json.dump(data, open('latest_telemetry.json', 'w'), indent=2)
print('AWS outage simulated')
"

# Watch AI engine respond
tail -f ai_engine.log
```

---

## Emergency Procedures

### Emergency: Runaway Costs

**Immediate Actions:**
1. Stop AI engine: `pkill -f engine.py`
2. Review current infrastructure: `terraform state list`
3. Identify expensive resources: Check AWS/Alibaba console
4. Destroy non-essential resources: `terraform destroy -target=module.service3`

**Prevention:**
- Set up billing alerts
- Implement hard spending limits
- Regular cost reviews

### Emergency: Service Outage

**Immediate Actions:**
1. Check health: `curl http://localhost:8000/healthz`
2. Review logs: `tail -100 ai-engine/ai_engine.log`
3. Restart services: `./start-all.sh`
4. Rollback if needed: `git revert HEAD && terraform apply`

**Escalation:**
- Contact on-call engineer
- Create incident in tracking system
- Follow incident response procedures

### Emergency: Data Loss

**Immediate Actions:**
1. Stop all services
2. Check backups: Terraform state, decision logs
3. Restore from backup if available
4. Document what was lost

**Prevention:**
- Regular backups of Terraform state
- Version control for all configurations
- Immutable decision logs

### Emergency: Security Breach

**Immediate Actions:**
1. Isolate affected systems
2. Rotate all credentials
3. Review access logs
4. Contact security team

**Follow-up:**
- Incident report
- Security audit
- Implement additional controls

---

## Maintenance Schedule

### Daily
- [ ] Check dashboard for anomalies
- [ ] Review AI decision log
- [ ] Monitor cost trends

### Weekly
- [ ] Review AI decision accuracy
- [ ] Check for unused resources
- [ ] Update documentation if needed

### Monthly
- [ ] Cost optimization review
- [ ] Policy effectiveness assessment
- [ ] Security audit
- [ ] Backup verification

### Quarterly
- [ ] Full system review
- [ ] Update dependencies
- [ ] Disaster recovery test
- [ ] Performance optimization

---

## Useful Commands Cheat Sheet

```bash
# Quick health check
curl -s http://localhost:8000/healthz | jq '.status'

# View latest AI decision
curl -s http://localhost:8000/api/decisions | jq '.decisions[-1]'

# Check current costs
curl -s http://localhost:8000/api/metrics | jq '.cost'

# List all services and providers
terraform output -json | jq '.deployment_summary.value.services'

# Restart everything
pkill -f "python|streamlit|uvicorn" && ./start-all.sh

# View logs in real-time
tail -f ai-engine/ai_engine.log

# Generate fresh telemetry
cd ai-engine && python simulator.py --sample
```

---

## Support & Contacts

- **Platform Team:** platform@swen.ai
- **On-Call:** +1-XXX-XXX-XXXX
- **Slack:** #swen-aiops
- **Documentation:** https://docs.swen.ai/aiops
- **Issue Tracker:** https://github.com/swen/swen-aio-test/issues

---

**Last Updated:** 2025-10-22  
**Maintained By:** Platform Engineering Team
