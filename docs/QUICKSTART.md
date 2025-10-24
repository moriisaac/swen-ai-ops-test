# 🚀 SWEN AIOps - Quick Start Guide

Get the platform running in under 5 minutes!

---

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check if pip is installed
pip3 --version

# Check Git
git --version
```

If any are missing, install them first.

---

## Installation (3 Steps)

### Step 1: Clone and Enter Directory

```bash
git clone https://github.com/swen/swen-aio-test.git
cd swen-aio-test
```

### Step 2: Start All Services

```bash
./start-all.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Generate initial telemetry data
- Start all 4 services (Simulator, AI Engine, API, Dashboard)

**Wait 30 seconds** for all services to initialize.

### Step 3: Open Dashboard

```bash
# On macOS/Linux
open http://localhost:8501

# Or manually navigate to:
# http://localhost:8501
```

---

## ✅ Verify Everything Works

### Check 1: API Health

```bash
curl http://localhost:8000/healthz
```

Expected output:
```json
{
  "status": "ok",
  "active_providers": ["aws", "alibaba"],
  "services": {
    "service1": "aws",
    "service2": "aws",
    "service3": "alibaba"
  }
}
```

### Check 2: Dashboard Loads

Open http://localhost:8501 in your browser. You should see:
- ✅ Overview tab with metrics
- ✅ Live telemetry data
- ✅ Service distribution chart

### Check 3: Telemetry Updates

Watch the dashboard for 10 seconds. Metrics should update automatically.

---

## 🎬 Run the Demo

### Self-Healing Demonstration

```bash
# In a new terminal
python ops/self_healing_demo.py
```

This will show:
1. Region outage recovery
2. Cost spike mitigation
3. Performance degradation response

Watch the dashboard while the demo runs to see live updates!

---

## 🛑 Stop Everything

```bash
./stop-all.sh
```

---

## 📊 What to Explore

### 1. Dashboard Tabs

- **Overview**: System status and key metrics
- **AI Decisions**: See what the AI engine recommends
- **Cost Analysis**: Compare AWS vs Alibaba costs
- **Telemetry**: Live metrics for each service
- **Live Feed**: Real-time activity stream

### 2. API Endpoints

```bash
# Get telemetry
curl http://localhost:8000/api/telemetry | jq

# Get AI decisions
curl http://localhost:8000/api/decisions | jq

# Get cost analysis
curl http://localhost:8000/api/cost-analysis | jq

# Get metrics summary
curl http://localhost:8000/api/metrics | jq
```

### 3. Logs

```bash
# View all logs
tail -f logs/*.log

# View specific service
tail -f logs/engine.log
```

---

## 🔧 Troubleshooting

### Services Won't Start

```bash
# Stop everything
./stop-all.sh

# Remove old logs
rm -rf logs/*.log

# Try again
./start-all.sh
```

### Dashboard Shows "Unable to fetch data"

```bash
# Check if API is running
curl http://localhost:8000/healthz

# If not, check API logs
tail -f logs/api.log

# Restart API
cd dashboard/api
python main.py
```

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
cd dashboard/api
PORT=8001 python main.py
```

---

## 🎯 Next Steps

1. **Read the Documentation**
   - [RUNBOOK.md](docs/RUNBOOK.md) - Complete operations guide
   - [POLICY.md](ops/POLICY.md) - Governance policies
   - [COST_STRATEGY.md](docs/COST_STRATEGY.md) - FinOps strategy

2. **Explore the Code**
   - `ai-engine/engine.py` - AI decision logic
   - `dashboard/api/main.py` - API endpoints
   - `dashboard/ui/app.py` - Dashboard UI

3. **Deploy to Cloud** (Optional)
   - See [README.md](README.md) for cloud deployment instructions
   - Configure Terraform for real AWS/Alibaba resources

4. **Customize**
   - Adjust AI scoring weights in `engine.py`
   - Modify policy thresholds in `ops/policy_gate.py`
   - Add new visualizations to dashboard

---

## 💡 Tips

- **Auto-refresh**: Dashboard refreshes every 10 seconds (configurable in sidebar)
- **Manual refresh**: Click "🔄 Refresh Now" button in dashboard
- **Simulate changes**: Edit `ai-engine/latest_telemetry.json` to trigger AI decisions
- **View decisions**: Check `ai-engine/ai_decisions.json` for decision history

---

## 📞 Need Help?

- Check [RUNBOOK.md](docs/RUNBOOK.md) for detailed troubleshooting
- Review logs in `logs/` directory
- Open an issue on GitHub

---

**You're all set! Enjoy exploring the SWEN AIOps platform! 🎉**
