# Testing Checklist for SWEN AIOps Platform

## Pre-Deployment Testing

### ✅ Environment Setup

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies can be installed
pip install -r ai-engine/requirements.txt --dry-run
pip install -r dashboard/api/requirements.txt --dry-run
pip install -r dashboard/ui/requirements.txt --dry-run

# Check Terraform is available (optional for local demo)
terraform --version  # Should be 1.0+
```

---

## Functional Testing

### 1. Service Startup Tests

```bash
# Test 1: Start all services
./start-all.sh

# Expected: All 4 services start without errors
# - Simulator (PID shown)
# - AI Engine (PID shown)
# - Dashboard API (PID shown)
# - Dashboard UI (PID shown)

# Verify PIDs file created
cat .pids  # Should show 4 PIDs

# Check logs directory created
ls -la logs/  # Should contain 4 log files
```

### 2. API Health Tests

```bash
# Test 2: API responds to health check
curl http://localhost:8000/healthz

# Expected output:
# {
#   "status": "ok",
#   "active_providers": ["aws", "alibaba"],
#   "services": {...}
# }

# Test 3: API documentation accessible
curl http://localhost:8000/docs
# Should return HTML (Swagger UI)

# Test 4: Telemetry endpoint
curl http://localhost:8000/api/telemetry | jq

# Expected: JSON with service telemetry data

# Test 5: Metrics endpoint (Prometheus format)
curl http://localhost:8000/metrics

# Expected: Prometheus-formatted metrics
```

### 3. Dashboard UI Tests

```bash
# Test 6: Dashboard loads
open http://localhost:8501

# Manual checks:
# ✓ Page loads without errors
# ✓ Overview tab shows metrics
# ✓ Service distribution chart displays
# ✓ Metrics update within 10 seconds
# ✓ All 5 tabs are accessible
```

### 4. Telemetry Generation Tests

```bash
# Test 7: Telemetry file exists and updates
ls -la ai-engine/latest_telemetry.json

# Watch for updates (should change every 5 seconds)
watch -n 1 "stat ai-engine/latest_telemetry.json"

# Test 8: Telemetry content is valid JSON
cat ai-engine/latest_telemetry.json | jq

# Expected: Valid JSON with service data
```

### 5. AI Engine Tests

```bash
# Test 9: AI engine creates decision log
ls -la ai-engine/ai_decisions.json

# Test 10: Engine logs are being written
tail -f ai-engine/ai_engine.log

# Expected: Log entries showing analysis

# Test 11: Manually trigger decision (optional)
python -c "
from ai_engine.engine import CostOptimizationEngine
engine = CostOptimizationEngine()
telemetry = engine._read_telemetry()
print('Telemetry loaded:', len(telemetry), 'services')
"
```

### 6. Self-Healing Demo Tests

```bash
# Test 12: Demo script runs
python ops/self_healing_demo.py

# Expected:
# ✓ Shows 3 scenarios
# ✓ Completes without errors
# ✓ Creates self_heal_event.log
# ✓ Updates telemetry during demo

# Test 13: Event log created
cat ops/self_heal_event.log | jq

# Expected: JSON lines with event data
```

### 7. Service Shutdown Tests

```bash
# Test 14: Stop all services
./stop-all.sh

# Expected:
# ✓ All processes stopped
# ✓ .pids file removed
# ✓ No orphaned processes

# Verify no processes running
ps aux | grep -E "simulator|engine|main.py|streamlit"
# Should return nothing (except grep itself)
```

---

## Integration Testing

### 8. End-to-End Data Flow

```bash
# Start services
./start-all.sh
sleep 30  # Wait for initialization

# Test 15: Data flows from simulator to dashboard
# 1. Check simulator is generating data
cat ai-engine/latest_telemetry.json | jq '.service1.aws.cost'

# 2. Verify API can read it
curl -s http://localhost:8000/api/telemetry | jq '.data.service1.aws.cost'

# 3. Check dashboard displays it (manual)
open http://localhost:8501
# Navigate to Telemetry tab, verify service1 shows data

# Test 16: AI decisions appear in dashboard
# Wait for AI engine to make a decision (may take a few minutes)
# Then check:
curl -s http://localhost:8000/api/decisions | jq '.decisions | length'
# Should be > 0 if decisions were made
```

### 9. WebSocket Testing

```bash
# Test 17: WebSocket connection (requires wscat)
# npm install -g wscat
wscat -c ws://localhost:8000/ws

# Expected: Receives periodic updates with telemetry data
# Press Ctrl+C to disconnect
```

---

## Performance Testing

### 10. Load Testing (Optional)

```bash
# Test 18: API can handle multiple requests
for i in {1..100}; do
  curl -s http://localhost:8000/healthz > /dev/null &
done
wait

# Check API is still responsive
curl http://localhost:8000/healthz

# Test 19: Dashboard handles concurrent users (manual)
# Open dashboard in 3 different browsers
# Verify all show data correctly
```

---

## Error Handling Tests

### 11. Graceful Degradation

```bash
# Test 20: API handles missing telemetry file
mv ai-engine/latest_telemetry.json ai-engine/latest_telemetry.json.bak
curl http://localhost:8000/api/telemetry
# Expected: 404 or empty data, not a crash

# Restore file
mv ai-engine/latest_telemetry.json.bak ai-engine/latest_telemetry.json

# Test 21: Dashboard handles API downtime
# Stop API
pkill -f "python.*main.py"

# Check dashboard (should show error message, not crash)
open http://localhost:8501

# Restart API
cd dashboard/api && python main.py &
```

---

## Terraform Testing (Optional)

### 12. Infrastructure Validation

```bash
# Test 22: Terraform configuration is valid
cd infra/envs/prod
terraform init
terraform validate

# Expected: Success message

# Test 23: Terraform plan runs (dry-run)
terraform plan

# Expected: Shows planned changes (no errors)
# Note: Don't apply unless you want to create real resources
```

---

## GitLab CI Testing (Optional)

### 13. Pipeline Validation

```bash
# Test 24: GitLab CI syntax is valid
# Install gitlab-ci-lint (if available)
# Or use GitLab's online validator

# Test 25: Policy gate script works
cd ops
python policy_gate.py

# Expected: Error (no metadata file)
# This is correct - it should fail without metadata

# Create sample metadata
cp ../infra/envs/prod/ai-metadata.json.example ../infra/envs/prod/ai-metadata.json

# Run again
python policy_gate.py

# Expected: Policy evaluation output
```

---

## Documentation Testing

### 14. Documentation Completeness

```bash
# Test 26: All referenced files exist
# Check README links
grep -o '\[.*\](.*.md)' README.md | sed 's/.*(\(.*\))/\1/' | while read file; do
  if [ ! -f "$file" ]; then
    echo "Missing: $file"
  fi
done

# Test 27: Code examples in docs are valid
# Extract and test code blocks (manual review)
```

---

## Security Testing

### 15. Security Checks

```bash
# Test 28: No hardcoded credentials
grep -r "password\|secret\|key" --include="*.py" --include="*.tf" .
# Review results - should only be variable names, not actual secrets

# Test 29: .gitignore covers sensitive files
cat .gitignore | grep -E "\.env|\.pem|\.key|credentials"
# Expected: These patterns are present

# Test 30: Logs don't contain sensitive data
grep -i "password\|secret\|key" logs/*.log 2>/dev/null
# Expected: No matches
```

---

## Final Checklist

### Pre-Submission Validation

- [ ] All services start successfully
- [ ] Dashboard loads and displays data
- [ ] API endpoints respond correctly
- [ ] Self-healing demo runs without errors
- [ ] Telemetry updates in real-time
- [ ] No errors in logs
- [ ] Documentation is complete
- [ ] No sensitive data in repository
- [ ] .gitignore is comprehensive
- [ ] README instructions are accurate

### Manual Testing Checklist

- [ ] Open dashboard in browser
- [ ] Navigate through all 5 tabs
- [ ] Verify charts render correctly
- [ ] Check metrics update automatically
- [ ] Review AI decisions tab
- [ ] Test cost analysis visualizations
- [ ] Verify telemetry shows live data
- [ ] Check live feed updates

### Demo Preparation

- [ ] Run `./start-all.sh` successfully
- [ ] Wait 30 seconds for initialization
- [ ] Open dashboard at http://localhost:8501
- [ ] Run self-healing demo in separate terminal
- [ ] Watch dashboard update during demo
- [ ] Take screenshots of key features
- [ ] Prepare talking points

---

## Test Results Template

```
Test Date: _______________
Tester: _______________

Startup Tests:        [ PASS / FAIL ]
API Tests:            [ PASS / FAIL ]
Dashboard Tests:      [ PASS / FAIL ]
Telemetry Tests:      [ PASS / FAIL ]
AI Engine Tests:      [ PASS / FAIL ]
Self-Healing Tests:   [ PASS / FAIL ]
Shutdown Tests:       [ PASS / FAIL ]
Integration Tests:    [ PASS / FAIL ]
Documentation Tests:  [ PASS / FAIL ]
Security Tests:       [ PASS / FAIL ]

Overall Status:       [ READY / NOT READY ]

Notes:
_________________________________
_________________________________
_________________________________
```

---

## Troubleshooting Common Issues

### Issue: Services won't start

```bash
# Solution 1: Check Python version
python3 --version

# Solution 2: Reinstall dependencies
pip install -r ai-engine/requirements.txt --force-reinstall

# Solution 3: Check ports are available
lsof -i :8000
lsof -i :8501
```

### Issue: Dashboard shows "Unable to fetch data"

```bash
# Solution: Verify API is running
curl http://localhost:8000/healthz

# If not running, check logs
tail -f logs/api.log
```

### Issue: Telemetry not updating

```bash
# Solution: Check simulator is running
ps aux | grep simulator.py

# Restart simulator
cd ai-engine
python simulator.py --interval 5 &
```

---

## Automated Test Script

```bash
#!/bin/bash
# run_tests.sh - Automated testing script

echo "Running SWEN AIOps Tests..."

# Test 1: Start services
./start-all.sh
sleep 30

# Test 2: Check API health
if curl -s http://localhost:8000/healthz | grep -q "ok"; then
  echo "✓ API health check passed"
else
  echo "✗ API health check failed"
  exit 1
fi

# Test 3: Check telemetry
if [ -f "ai-engine/latest_telemetry.json" ]; then
  echo "✓ Telemetry file exists"
else
  echo "✗ Telemetry file missing"
  exit 1
fi

# Test 4: Run self-healing demo
if python ops/self_healing_demo.py; then
  echo "✓ Self-healing demo passed"
else
  echo "✗ Self-healing demo failed"
  exit 1
fi

# Test 5: Stop services
./stop-all.sh

echo "All tests passed! ✓"
```

---

**Testing Complete!** 🎉

All tests should pass before submission. If any test fails, refer to the troubleshooting section or the RUNBOOK.md for detailed guidance.
