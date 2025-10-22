#!/bin/bash
# SWEN AIOps Platform - Stop All Services

echo "=================================================="
echo "  SWEN AIOps Platform - Stopping All Services"
echo "=================================================="
echo ""

# Check if PID file exists
if [ -f ".pids" ]; then
    echo "Stopping services..."
    
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Stopping process $pid..."
            kill $pid 2>/dev/null || true
        fi
    done < .pids
    
    # Wait for processes to stop
    sleep 2
    
    # Force kill if still running
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Force stopping process $pid..."
            kill -9 $pid 2>/dev/null || true
        fi
    done < .pids
    
    rm .pids
    echo ""
    echo "✓ All services stopped"
else
    echo "No PID file found. Attempting to stop by process name..."
    
    pkill -f "python.*simulator.py" || true
    pkill -f "python.*engine.py" || true
    pkill -f "python.*main.py" || true
    pkill -f "streamlit" || true
    
    echo "✓ Processes stopped"
fi

echo ""
echo "=================================================="
echo "  Platform Stopped"
echo "=================================================="
