#!/bin/bash
# Enhanced Self-Healing Monitor with Branch Management
# Monitors system health and performs automatic healing including branch management

set -e

echo "🔄 Enhanced Self-Healing Monitor with Branch Management"
echo "======================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MONITOR_INTERVAL=${MONITOR_INTERVAL:-60}
LOG_FILE="logs/self_healing.log"
REPO_PATH=$(dirname "$0")/..

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to check system health
check_system_health() {
    log_message "INFO" "🔍 Checking system health..."
    
    local health_status="healthy"
    local issues=()
    
    # Check API health
    if curl -s -f "http://localhost:8001/healthz" > /dev/null 2>&1; then
        log_message "INFO" "✅ API is healthy"
    else
        log_message "WARN" "❌ API is not responding"
        health_status="degraded"
        issues+=("API")
    fi
    
    # Check AI Engine health
    if pgrep -f "engine.py" > /dev/null; then
        log_message "INFO" "✅ AI Engine is running"
    else
        log_message "WARN" "❌ AI Engine is not running"
        health_status="degraded"
        issues+=("AI_Engine")
    fi
    
    # Check Telemetry Simulator
    if pgrep -f "simulator.py" > /dev/null; then
        log_message "INFO" "✅ Telemetry Simulator is running"
    else
        log_message "WARN" "❌ Telemetry Simulator is not running"
        health_status="degraded"
        issues+=("Simulator")
    fi
    
    # Check Branch Management
    local branch_count=$(git branch -r | grep "ai-recommendation" | wc -l | xargs)
    local max_branches=5
    
    if [ "$branch_count" -le "$max_branches" ]; then
        log_message "INFO" "✅ Branch count healthy: $branch_count/$max_branches"
    else
        log_message "WARN" "⚠️ Branch count exceeded: $branch_count/$max_branches"
        health_status="degraded"
        issues+=("Branch_Management")
    fi
    
    # Check Dashboard UI
    if pgrep -f "streamlit.*app.py" > /dev/null; then
        log_message "INFO" "✅ Dashboard UI is running"
    else
        log_message "WARN" "❌ Dashboard UI is not running"
        health_status="degraded"
        issues+=("Dashboard")
    fi
    
    echo "$health_status"
    if [ ${#issues[@]} -gt 0 ]; then
        echo "${issues[*]}"
    fi
}

# Function to heal API issues
heal_api() {
    log_message "HEAL" "🔧 Attempting to heal API..."
    
    # Kill existing API process
    pkill -f "main.py" 2>/dev/null || true
    sleep 2
    
    # Start API
    cd "$REPO_PATH/dashboard/api"
    nohup python main.py > ../../logs/api.log 2>&1 &
    API_PID=$!
    
    sleep 5
    
    # Check if API is now healthy
    if curl -s -f "http://localhost:8001/healthz" > /dev/null 2>&1; then
        log_message "SUCCESS" "✅ API healing successful (PID: $API_PID)"
        return 0
    else
        log_message "FAILED" "❌ API healing failed"
        return 1
    fi
}

# Function to heal AI Engine
heal_ai_engine() {
    log_message "HEAL" "🔧 Attempting to heal AI Engine..."
    
    # Kill existing AI engine process
    pkill -f "engine.py" 2>/dev/null || true
    sleep 2
    
    # Start AI Engine
    cd "$REPO_PATH/ai-engine"
    nohup python engine.py > ../logs/engine.log 2>&1 &
    ENGINE_PID=$!
    
    sleep 5
    
    # Check if AI Engine is now running
    if pgrep -f "engine.py" > /dev/null; then
        log_message "SUCCESS" "✅ AI Engine healing successful (PID: $ENGINE_PID)"
        return 0
    else
        log_message "FAILED" "❌ AI Engine healing failed"
        return 1
    fi
}

# Function to heal Telemetry Simulator
heal_simulator() {
    log_message "HEAL" "🔧 Attempting to heal Telemetry Simulator..."
    
    # Kill existing simulator process
    pkill -f "simulator.py" 2>/dev/null || true
    sleep 2
    
    # Start Simulator
    cd "$REPO_PATH/ai-engine"
    nohup python simulator.py --interval 5 > ../logs/simulator.log 2>&1 &
    SIMULATOR_PID=$!
    
    sleep 5
    
    # Check if Simulator is now running
    if pgrep -f "simulator.py" > /dev/null; then
        log_message "SUCCESS" "✅ Simulator healing successful (PID: $SIMULATOR_PID)"
        return 0
    else
        log_message "FAILED" "❌ Simulator healing failed"
        return 1
    fi
}

# Function to heal branch management issues
heal_branch_management() {
    log_message "HEAL" "🔧 Attempting to heal branch management..."
    
    local branch_count=$(git branch -r | grep "ai-recommendation" | wc -l | xargs)
    local max_branches=5
    
    if [ "$branch_count" -gt "$max_branches" ]; then
        log_message "HEAL" "🗑️ Cleaning up excess branches ($branch_count > $max_branches)"
        
        # Get the most recent branches to keep
        local keep_branches=$(git branch -r | grep "ai-recommendation" | sort -k2 -r | head -5 | sed 's/origin\///')
        
        # Delete excess branches
        local branches_to_delete=$(git branch -r | grep "ai-recommendation" | sed 's/origin\///' | grep -v -F "$keep_branches")
        
        if [ -n "$branches_to_delete" ]; then
            echo "$branches_to_delete" | xargs -n 1 git push origin --delete 2>/dev/null || true
            log_message "SUCCESS" "✅ Branch cleanup completed"
        else
            log_message "INFO" "ℹ️ No branches to delete"
        fi
        
        # Verify cleanup
        local new_count=$(git branch -r | grep "ai-recommendation" | wc -l | xargs)
        log_message "SUCCESS" "📊 Branch count: $branch_count → $new_count"
        
        return 0
    else
        log_message "INFO" "ℹ️ Branch count is healthy: $branch_count/$max_branches"
        return 0
    fi
}

# Function to heal Dashboard UI
heal_dashboard() {
    log_message "HEAL" "🔧 Attempting to heal Dashboard UI..."
    
    # Kill existing dashboard process
    pkill -f "streamlit.*app.py" 2>/dev/null || true
    sleep 2
    
    # Start Dashboard
    cd "$REPO_PATH/dashboard/ui"
    nohup streamlit run app.py --server.port 8501 --server.headless true > ../../logs/ui.log 2>&1 &
    DASHBOARD_PID=$!
    
    sleep 5
    
    # Check if Dashboard is now running
    if pgrep -f "streamlit.*app.py" > /dev/null; then
        log_message "SUCCESS" "✅ Dashboard healing successful (PID: $DASHBOARD_PID)"
        return 0
    else
        log_message "FAILED" "❌ Dashboard healing failed"
        return 1
    fi
}

# Function to perform self-healing
perform_self_healing() {
    local health_result=$(check_system_health)
    local health_status=$(echo "$health_result" | head -1)
    local issues=$(echo "$health_result" | tail -n +2)
    
    if [ "$health_status" = "healthy" ]; then
        log_message "INFO" "✅ System is healthy, no healing needed"
        return 0
    fi
    
    log_message "HEAL" "🚨 System health degraded, performing self-healing..."
    log_message "HEAL" "Issues detected: $issues"
    
    local healing_success=true
    
    # Heal each issue
    for issue in $issues; do
        case $issue in
            "API")
                if ! heal_api; then
                    healing_success=false
                fi
                ;;
            "AI_Engine")
                if ! heal_ai_engine; then
                    healing_success=false
                fi
                ;;
            "Simulator")
                if ! heal_simulator; then
                    healing_success=false
                fi
                ;;
            "Branch_Management")
                if ! heal_branch_management; then
                    healing_success=false
                fi
                ;;
            "Dashboard")
                if ! heal_dashboard; then
                    healing_success=false
                fi
                ;;
        esac
    done
    
    if [ "$healing_success" = true ]; then
        log_message "SUCCESS" "✅ Self-healing completed successfully"
    else
        log_message "FAILED" "❌ Self-healing completed with some failures"
    fi
    
    return $([ "$healing_success" = true ] && echo 0 || echo 1)
}

# Function to run continuous monitoring
run_monitoring() {
    log_message "INFO" "🔄 Starting continuous monitoring (interval: ${MONITOR_INTERVAL}s)"
    log_message "INFO" "Press Ctrl+C to stop monitoring"
    
    while true; do
        perform_self_healing
        sleep "$MONITOR_INTERVAL"
    done
}

# Function to show current status
show_status() {
    echo -e "${BLUE}📊 Current System Status${NC}"
    echo "========================"
    
    local health_result=$(check_system_health)
    local health_status=$(echo "$health_result" | head -1)
    local issues=$(echo "$health_result" | tail -n +2)
    
    if [ "$health_status" = "healthy" ]; then
        echo -e "${GREEN}✅ System Status: HEALTHY${NC}"
    else
        echo -e "${RED}❌ System Status: DEGRADED${NC}"
        echo -e "${YELLOW}Issues: $issues${NC}"
    fi
    
    echo ""
    echo "Service Status:"
    echo "--------------"
    
    # API Status
    if curl -s -f "http://localhost:8001/healthz" > /dev/null 2>&1; then
        echo -e "API: ${GREEN}✅ Running${NC}"
    else
        echo -e "API: ${RED}❌ Not responding${NC}"
    fi
    
    # AI Engine Status
    if pgrep -f "engine.py" > /dev/null; then
        echo -e "AI Engine: ${GREEN}✅ Running${NC}"
    else
        echo -e "AI Engine: ${RED}❌ Not running${NC}"
    fi
    
    # Simulator Status
    if pgrep -f "simulator.py" > /dev/null; then
        echo -e "Simulator: ${GREEN}✅ Running${NC}"
    else
        echo -e "Simulator: ${RED}❌ Not running${NC}"
    fi
    
    # Dashboard Status
    if pgrep -f "streamlit.*app.py" > /dev/null; then
        echo -e "Dashboard: ${GREEN}✅ Running${NC}"
    else
        echo -e "Dashboard: ${RED}❌ Not running${NC}"
    fi
    
    # Branch Status
    local branch_count=$(git branch -r | grep "ai-recommendation" | wc -l | xargs)
    local max_branches=5
    if [ "$branch_count" -le "$max_branches" ]; then
        echo -e "Branches: ${GREEN}✅ $branch_count/$max_branches${NC}"
    else
        echo -e "Branches: ${RED}❌ $branch_count/$max_branches (exceeded)${NC}"
    fi
}

# Main script logic
case "${1:-status}" in
    "status")
        show_status
        ;;
    "heal")
        perform_self_healing
        ;;
    "monitor")
        run_monitoring
        ;;
    "health")
        check_system_health
        ;;
    *)
        echo "Usage: $0 {status|heal|monitor|health}"
        echo ""
        echo "Commands:"
        echo "  status  - Show current system status"
        echo "  heal    - Perform self-healing once"
        echo "  monitor - Run continuous monitoring"
        echo "  health  - Check system health only"
        echo ""
        echo "Environment Variables:"
        echo "  MONITOR_INTERVAL - Monitoring interval in seconds (default: 60)"
        exit 1
        ;;
esac
