# SWEN AIOps - Quick Command Reference

Essential commands for operating the SWEN AIOps platform.

---

## 🚀 Getting Started

### Start Everything
```bash
./start-all.sh
```

### Stop Everything
```bash
./stop-all.sh
```

### Access Dashboard
```bash
open http://localhost:8501
# Or navigate to: http://localhost:8501 in your browser
```

---

## 🔍 Health Checks

### Check API Health
```bash
curl http://localhost:8000/healthz | jq
```

### Check All Services Running
```bash
ps aux | grep -E "simulator|engine|main.py|streamlit"
```

### View Service PIDs
```bash
cat .pids
```

---

## 📊 API Endpoints

### Get Telemetry Data
```bash
curl http://localhost:8000/api/telemetry | jq
```

### Get AI Decisions
```bash
curl http://localhost:8000/api/decisions | jq
```

### Get Latest Decision
```bash
curl http://localhost:8000/api/decisions | jq '.decisions[-1]'
```

### Get Metrics Summary
```bash
curl http://localhost:8000/api/metrics | jq
```

### Get Cost Analysis
```bash
curl http://localhost:8000/api/cost-analysis | jq
```

### Get Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

---

## 📝 Logs

### View All Logs
```bash
tail -f logs/*.log
```

### View Specific Service Logs
```bash
# Simulator
tail -f logs/simulator.log

# AI Engine
tail -f logs/engine.log

# API
tail -f logs/api.log

# Dashboard
tail -f logs/ui.log
```

### View AI Engine Decision Log
```bash
cat ai-engine/ai_engine.log
```

### View Latest Telemetry
```bash
cat ai-engine/latest_telemetry.json | jq
```

### View Decision History
```bash
cat ai-engine/ai_decisions.json | jq
```

---

## 🎬 Demonstrations

### Run Self-Healing Demo
```bash
python ops/self_healing_demo.py
```

### Generate Sample Telemetry
```bash
cd ai-engine
python simulator.py --sample --output latest_telemetry.json
```

### Manually Trigger AI Analysis
```bash
python -c "
from ai_engine.engine import CostOptimizationEngine
engine = CostOptimizationEngine()
telemetry = engine._read_telemetry()
for service, metrics in telemetry.items():
    provider, decision = engine.make_decision(service, metrics)
    if provider:
        print(f'{service}: Recommend {provider}')
        print(f'Confidence: {decision[\"confidence\"]:.2%}')
"
```

---

## 🏗️ Infrastructure (Terraform)

### Initialize Terraform
```bash
cd infra/envs/prod
terraform init
```

### Validate Configuration
```bash
terraform validate
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
terraform output -json
```

### Destroy Infrastructure
```bash
terraform destroy
```

---

## 🔧 Development

### Install Dependencies
```bash
# AI Engine
pip install -r ai-engine/requirements.txt

# Dashboard API
pip install -r dashboard/api/requirements.txt

# Dashboard UI
pip install -r dashboard/ui/requirements.txt
```

### Run Individual Services

#### Telemetry Simulator
```bash
cd ai-engine
python simulator.py --interval 5
```

#### AI Engine
```bash
cd ai-engine
python engine.py
```

#### Dashboard API
```bash
cd dashboard/api
python main.py
# Or with uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Dashboard UI
```bash
cd dashboard/ui
streamlit run app.py --server.port 8501
```

---

## 🧪 Testing

### Run All Tests
```bash
# If you create a test suite
pytest tests/
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/healthz

# Telemetry
curl http://localhost:8000/api/telemetry

# Decisions
curl http://localhost:8000/api/decisions

# Metrics
curl http://localhost:8000/api/metrics
```

### Load Test API
```bash
# Simple load test (100 requests)
for i in {1..100}; do
  curl -s http://localhost:8000/healthz > /dev/null &
done
wait
echo "Load test complete"
```

---

## 🐛 Debugging

### Check Port Usage
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check if port 8501 is in use
lsof -i :8501
```

### Kill Specific Process
```bash
# Kill by PID
kill <PID>

# Force kill
kill -9 <PID>

# Kill by name
pkill -f "simulator.py"
pkill -f "engine.py"
pkill -f "main.py"
pkill -f "streamlit"
```

### Clear Logs
```bash
rm -rf logs/*.log
```

### Reset State
```bash
# Stop services
./stop-all.sh

# Clear logs
rm -rf logs/*.log

# Reset decision history
echo "[]" > ai-engine/ai_decisions.json

# Remove telemetry
rm -f ai-engine/latest_telemetry.json

# Restart
./start-all.sh
```

---

## 📦 Git Operations

### Initialize Repository
```bash
git init
git add .
git commit -m "Initial commit: SWEN AIOps platform"
```

### Add Remote
```bash
git remote add origin https://github.com/yourusername/swen-aio-test.git
```

### Push to Remote
```bash
git push -u origin main
```

### Check Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

---

## 📊 Monitoring

### Watch Telemetry Updates
```bash
watch -n 1 "cat ai-engine/latest_telemetry.json | jq '.service1.aws.cost'"
```

### Monitor API Requests
```bash
tail -f logs/api.log | grep "GET\|POST"
```

### Watch Decision Count
```bash
watch -n 5 "curl -s http://localhost:8000/api/decisions | jq '.total'"
```

### Monitor System Resources
```bash
# CPU and memory usage
top

# Or with htop
htop
```

---

## 🔐 Security

### Check for Hardcoded Secrets
```bash
grep -r "password\|secret\|key" --include="*.py" --include="*.tf" .
```

### Verify .gitignore
```bash
cat .gitignore
```

### Check File Permissions
```bash
ls -la ai-engine/
ls -la dashboard/
ls -la infra/
```

---

## 📚 Documentation

### View Documentation
```bash
# Main README
cat README.md

# Quick start
cat QUICKSTART.md

# Runbook
cat docs/RUNBOOK.md

# Policy
cat ops/POLICY.md

# Cost strategy
cat docs/COST_STRATEGY.md

# Architecture
cat docs/ARCHITECTURE.md
```

### Generate Documentation (if using tools)
```bash
# Example: Generate API docs
cd dashboard/api
python -m pydoc -w main
```

---

## 🎯 Quick Workflows

### Complete Startup Workflow
```bash
# 1. Start services
./start-all.sh

# 2. Wait for initialization
sleep 30

# 3. Verify health
curl http://localhost:8000/healthz | jq

# 4. Open dashboard
open http://localhost:8501

# 5. Run demo (in new terminal)
python ops/self_healing_demo.py
```

### Development Workflow
```bash
# 1. Make changes to code
vim ai-engine/engine.py

# 2. Stop services
./stop-all.sh

# 3. Restart services
./start-all.sh

# 4. Check logs for errors
tail -f logs/engine.log
```

### Debugging Workflow
```bash
# 1. Check what's running
ps aux | grep -E "simulator|engine|main|streamlit"

# 2. Check logs
tail -f logs/*.log

# 3. Test API manually
curl http://localhost:8000/healthz

# 4. Restart if needed
./stop-all.sh
./start-all.sh
```

---

## 💡 Pro Tips

### Create Aliases (add to ~/.bashrc or ~/.zshrc)
```bash
alias swen-start='cd /Users/Mori/Desktop/Work/swen-ai/swen-aio-test && ./start-all.sh'
alias swen-stop='cd /Users/Mori/Desktop/Work/swen-ai/swen-aio-test && ./stop-all.sh'
alias swen-logs='cd /Users/Mori/Desktop/Work/swen-ai/swen-aio-test && tail -f logs/*.log'
alias swen-dash='open http://localhost:8501'
alias swen-health='curl http://localhost:8000/healthz | jq'
```

### Quick Status Check
```bash
# One-liner to check everything
curl -s http://localhost:8000/healthz | jq && \
echo "Dashboard: http://localhost:8501" && \
ps aux | grep -E "simulator|engine|main|streamlit" | grep -v grep | wc -l | xargs echo "Services running:"
```

### Export Data
```bash
# Export current state
mkdir -p exports
curl http://localhost:8000/api/telemetry > exports/telemetry_$(date +%Y%m%d_%H%M%S).json
curl http://localhost:8000/api/decisions > exports/decisions_$(date +%Y%m%d_%H%M%S).json
curl http://localhost:8000/api/metrics > exports/metrics_$(date +%Y%m%d_%H%M%S).json
```

---

## 🆘 Emergency Commands

### Force Stop Everything
```bash
pkill -9 -f "python.*simulator"
pkill -9 -f "python.*engine"
pkill -9 -f "python.*main"
pkill -9 -f "streamlit"
rm -f .pids
```

### Reset to Clean State
```bash
./stop-all.sh
rm -rf logs/
rm -f ai-engine/latest_telemetry.json
rm -f ai-engine/ai_decisions.json
rm -f .pids
./start-all.sh
```

### Backup Current State
```bash
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp ai-engine/latest_telemetry.json backups/$(date +%Y%m%d_%H%M%S)/
cp ai-engine/ai_decisions.json backups/$(date +%Y%m%d_%H%M%S)/
cp -r logs/ backups/$(date +%Y%m%d_%H%M%S)/
```

---

**Quick Reference Complete!** 📋

For detailed explanations, see:
- **Setup:** QUICKSTART.md
- **Operations:** docs/RUNBOOK.md
- **Troubleshooting:** docs/RUNBOOK.md (Troubleshooting section)
