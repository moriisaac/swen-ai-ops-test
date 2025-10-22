#!/bin/bash
# SWEN AIOps Platform - Start All Services
# This script starts all components of the platform

set -e

echo "=================================================="
echo "  SWEN AIOps Platform - Starting All Services"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r ai-engine/requirements.txt
    pip install -q -r dashboard/api/requirements.txt
    pip install -q -r dashboard/ui/requirements.txt
else
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p logs
mkdir -p ai-engine
mkdir -p dashboard/api
mkdir -p dashboard/ui

# Generate initial telemetry if it doesn't exist
if [ ! -f "ai-engine/latest_telemetry.json" ]; then
    echo -e "${YELLOW}Generating initial telemetry...${NC}"
    cd ai-engine
    python simulator.py --sample --output latest_telemetry.json
    cd ..
fi

# Initialize decision log if it doesn't exist
if [ ! -f "ai-engine/ai_decisions.json" ]; then
    echo "[]" > ai-engine/ai_decisions.json
fi

echo ""
echo "Starting services..."
echo ""

# Start Telemetry Simulator
echo -e "${GREEN}[1/4] Starting Telemetry Simulator...${NC}"
cd ai-engine
nohup python simulator.py --interval 5 > ../logs/simulator.log 2>&1 &
SIMULATOR_PID=$!
echo "  ✓ Simulator started (PID: $SIMULATOR_PID)"
cd ..

sleep 2

# Start AI Engine
echo -e "${GREEN}[2/4] Starting AI Engine...${NC}"
cd ai-engine
nohup python engine.py > ../logs/engine.log 2>&1 &
ENGINE_PID=$!
echo "  ✓ AI Engine started (PID: $ENGINE_PID)"
cd ..

sleep 2

# Start Dashboard API
echo -e "${GREEN}[3/4] Starting Dashboard API...${NC}"
cd dashboard/api
nohup python main.py > ../../logs/api.log 2>&1 &
API_PID=$!
echo "  ✓ Dashboard API started (PID: $API_PID)"
cd ../..

sleep 3

# Start Dashboard UI
echo -e "${GREEN}[4/4] Starting Dashboard UI...${NC}"
cd dashboard/ui
nohup streamlit run app.py --server.port 8501 --server.headless true > ../../logs/ui.log 2>&1 &
UI_PID=$!
echo "  ✓ Dashboard UI started (PID: $UI_PID)"
cd ../..

# Save PIDs to file for easy shutdown
echo "$SIMULATOR_PID" > .pids
echo "$ENGINE_PID" >> .pids
echo "$API_PID" >> .pids
echo "$UI_PID" >> .pids

echo ""
echo "=================================================="
echo "  All Services Started Successfully!"
echo "=================================================="
echo ""
echo "Access Points:"
echo "  Dashboard UI:  http://localhost:8501"
echo "  API Docs:      http://localhost:8001/docs"
echo "  Health Check:  http://localhost:8001/healthz"
echo ""
echo "Logs:"
echo "  Simulator:     logs/simulator.log"
echo "  AI Engine:     logs/engine.log"
echo "  API:           logs/api.log"
echo "  Dashboard:     logs/ui.log"
echo ""
echo "To stop all services, run:"
echo "  ./stop-all.sh"
echo ""
echo "To view logs in real-time:"
echo "  tail -f logs/*.log"
echo ""
echo "=================================================="

# Wait a moment for services to start
sleep 3

# Check if services are running
echo "Checking service health..."
if curl -s http://localhost:8001/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}⚠ API may still be starting...${NC}"
fi

echo ""
echo "Platform is ready! Open http://localhost:8501 in your browser."
