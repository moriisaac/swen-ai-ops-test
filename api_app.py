#!/usr/bin/env python3
"""
SWEN AIOps API Backend - Streamlit App
FastAPI backend service running as Streamlit app
"""

import streamlit as st
import uvicorn
import threading
import time
import requests
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app
app = FastAPI(title="SWEN AIOps API", version="1.0.0")

# Global state for dynamic data
if 'api_data' not in st.session_state:
    st.session_state.api_data = {
        'decisions_count': 15,
        'auto_approved': 12,
        'escalated': 3,
        'current_spend': 2500.0,
        'budget_utilization': 25.0
    }

# FastAPI endpoints
@app.get("/healthz")
async def health_check():
    return {
        "status": "ok",
        "active_providers": ["aws", "alibaba"],
        "services": {"service1": "aws", "service2": "alibaba", "service3": "aws"},
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/telemetry")
async def get_telemetry():
    return {
        "service1": {
            "current_provider": "aws",
            "aws": {
                "cost": round(random.uniform(0.3, 0.6), 2),
                "latency": round(random.uniform(10, 20), 1),
                "credits": round(random.uniform(0.7, 0.95), 2),
                "available_gpus": random.randint(4, 10),
                "cpu_utilization": round(random.uniform(50, 80), 1),
                "memory_utilization": round(random.uniform(60, 85), 1),
                "network_io": round(random.uniform(300, 600), 1),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "instance": random.choice(["m5.large", "m5.xlarge", "c5.large"])
            },
            "alibaba": {
                "cost": round(random.uniform(0.25, 0.55), 2),
                "latency": round(random.uniform(12, 22), 1),
                "credits": round(random.uniform(0.8, 0.98), 2),
                "available_gpus": random.randint(3, 8),
                "cpu_utilization": round(random.uniform(45, 75), 1),
                "memory_utilization": round(random.uniform(55, 80), 1),
                "network_io": round(random.uniform(250, 550), 1),
                "region": random.choice(["ap-southeast-1", "ap-northeast-1", "ap-south-1"]),
                "instance": random.choice(["ecs.c5.large", "ecs.c6.large", "ecs.g5.large"])
            }
        },
        "service2": {
            "current_provider": "alibaba",
            "aws": {
                "cost": round(random.uniform(0.4, 0.7), 2),
                "latency": round(random.uniform(15, 25), 1),
                "credits": round(random.uniform(0.6, 0.9), 2),
                "available_gpus": random.randint(2, 6),
                "cpu_utilization": round(random.uniform(60, 85), 1),
                "memory_utilization": round(random.uniform(65, 90), 1),
                "network_io": round(random.uniform(400, 700), 1),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "instance": random.choice(["m5.large", "m5.xlarge", "c5.large"])
            },
            "alibaba": {
                "cost": round(random.uniform(0.3, 0.6), 2),
                "latency": round(random.uniform(10, 20), 1),
                "credits": round(random.uniform(0.7, 0.95), 2),
                "available_gpus": random.randint(4, 9),
                "cpu_utilization": round(random.uniform(50, 75), 1),
                "memory_utilization": round(random.uniform(60, 85), 1),
                "network_io": round(random.uniform(300, 600), 1),
                "region": random.choice(["ap-southeast-1", "ap-northeast-1", "ap-south-1"]),
                "instance": random.choice(["ecs.c5.large", "ecs.c6.large", "ecs.g5.large"])
            }
        },
        "service3": {
            "current_provider": "aws",
            "aws": {
                "cost": round(random.uniform(0.35, 0.65), 2),
                "latency": round(random.uniform(8, 18), 1),
                "credits": round(random.uniform(0.75, 0.95), 2),
                "available_gpus": random.randint(5, 12),
                "cpu_utilization": round(random.uniform(45, 75), 1),
                "memory_utilization": round(random.uniform(55, 80), 1),
                "network_io": round(random.uniform(280, 580), 1),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "instance": random.choice(["m5.large", "m5.xlarge", "c5.large"])
            },
            "alibaba": {
                "cost": round(random.uniform(0.28, 0.58), 2),
                "latency": round(random.uniform(11, 21), 1),
                "credits": round(random.uniform(0.8, 0.98), 2),
                "available_gpus": random.randint(4, 10),
                "cpu_utilization": round(random.uniform(40, 70), 1),
                "memory_utilization": round(random.uniform(50, 75), 1),
                "network_io": round(random.uniform(250, 550), 1),
                "region": random.choice(["ap-southeast-1", "ap-northeast-1", "ap-south-1"]),
                "instance": random.choice(["ecs.c5.large", "ecs.c6.large", "ecs.g5.large"])
            }
        }
    }

@app.get("/api/decisions")
async def get_decisions():
    decisions = []
    for i in range(st.session_state.api_data['decisions_count']):
        services = ["service1", "service2", "service3"]
        providers = ["aws", "alibaba"]
        
        service = random.choice(services)
        from_provider = random.choice(providers)
        to_provider = random.choice([p for p in providers if p != from_provider])
        
        reasons = [
            f"Cost optimization: {to_provider.upper()} offers {random.randint(15, 30)}% lower cost",
            f"Performance improvement: {to_provider.upper()} shows {random.randint(20, 40)}% better latency",
            f"Resource availability: {to_provider.upper()} has {random.randint(2, 5)} more GPUs available",
            f"Credit utilization: {to_provider.upper()} has better credit balance"
        ]
        
        confidence = round(random.uniform(0.75, 0.95), 2)
        predicted_savings = round(random.uniform(0.05, 0.15), 2)
        cost_delta_percent = round(random.uniform(2, 8), 1)
        
        # Policy evaluation
        if confidence >= 0.85 and predicted_savings >= 0.05 and cost_delta_percent <= 5:
            policy_status = "auto_approved"
            policy_reasoning = f"Auto-approved: All policy criteria met (confidence: {confidence:.1%}, savings: ${predicted_savings:.2f}/month)"
            policy_violations = []
        else:
            policy_status = "escalated"
            violations = []
            if confidence < 0.85:
                violations.append(f"Confidence {confidence:.1%} below 85% threshold")
            if predicted_savings < 0.05:
                violations.append(f"Predicted savings ${predicted_savings:.2f} below $0.05 threshold")
            if cost_delta_percent > 5:
                violations.append(f"Cost delta {cost_delta_percent:.1f}% exceeds 5% threshold")
            policy_reasoning = f"Escalated for manual review: {len(violations)} policy violations"
            policy_violations = violations
        
        decisions.append({
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat() + "Z",
            "service": service,
            "action": "move",
            "from_provider": from_provider,
            "to_provider": to_provider,
            "reason": random.choice(reasons),
            "confidence": confidence,
            "estimated_savings": predicted_savings,
            "git_branch": f"ai-recommendation/{service}-{int(datetime.now().timestamp()) - random.randint(1000, 10000)}",
            "commit_sha": f"{random.randint(100000, 999999):06x}",
            "policy_status": policy_status,
            "policy_reasoning": policy_reasoning,
            "policy_violations": policy_violations,
            "cost_delta_percent": cost_delta_percent,
            "budget_impact": round(random.uniform(-0.1, 0.1), 2),
            "credit_utilization": round(random.uniform(0, 0.05), 2)
        })
    
    return {"decisions": decisions, "total": len(decisions)}

@app.get("/api/cost-analysis")
async def get_cost_analysis():
    return {
        "total_cost": round(random.uniform(1.2, 1.8), 2),
        "aws_cost": round(random.uniform(0.7, 1.1), 2),
        "alibaba_cost": round(random.uniform(0.4, 0.8), 2),
        "savings_potential": round(random.uniform(0.15, 0.25), 2),
        "trend": random.choice(["decreasing", "stable", "increasing"]),
        "analysis": {
            "aws": {
                "services": random.randint(1, 2),
                "total_cost": round(random.uniform(0.7, 1.1), 2),
                "avg_latency": round(random.uniform(10, 20), 1),
                "credits": round(random.uniform(0.7, 0.9), 2),
                "discounts": round(random.uniform(0.03, 0.06), 2)
            },
            "alibaba": {
                "services": random.randint(1, 2),
                "total_cost": round(random.uniform(0.4, 0.8), 2),
                "avg_latency": round(random.uniform(12, 22), 1),
                "credits": round(random.uniform(0.8, 0.95), 2),
                "discounts": round(random.uniform(0.04, 0.07), 2)
            }
        },
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/policy-visibility")
async def get_policy_visibility():
    return {
        "policy_stats": {
            "auto_approved": st.session_state.api_data['auto_approved'],
            "escalated": st.session_state.api_data['escalated'],
            "pending": 0,
            "total": st.session_state.api_data['decisions_count']
        },
        "recent_decisions": [
            {
                "timestamp": datetime.now().isoformat(),
                "service": random.choice(["service1", "service2", "service3"]),
                "policy_status": random.choice(["auto_approved", "escalated"]),
                "reasoning": "All policy criteria met (confidence: 87%, savings: $0.07/month)",
                "predicted_savings": round(random.uniform(0.05, 0.15), 2)
            }
        ],
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/gitops-history")
async def get_gitops_history():
    return {
        "gitops_history": [
            {
                "timestamp": datetime.now().isoformat(),
                "service": random.choice(["service1", "service2", "service3"]),
                "action": "move",
                "git_branch": f"ai-recommendation/service{random.randint(1,3)}-{int(datetime.now().timestamp())}",
                "commit_hash": f"{random.randint(100000, 999999):06x}",
                "reasoning": "Cost optimization: AWS offers 18% lower cost with similar performance",
                "predicted_savings": round(random.uniform(0.05, 0.15), 2),
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "policy_status": random.choice(["auto_approved", "escalated"])
            }
        ],
        "total_commits": st.session_state.api_data['decisions_count'],
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/economics-view")
async def get_economics_view():
    hourly_spend = round(random.uniform(1.2, 1.8), 2)
    return {
        "total_spend": {
            "hourly": hourly_spend,
            "monthly": round(hourly_spend * 24 * 30, 2),
            "daily": round(hourly_spend * 24, 2)
        },
        "provider_breakdown": {
            "aws": {
                "hourly": round(hourly_spend * 0.6, 2),
                "monthly": round(hourly_spend * 0.6 * 24 * 30, 2),
                "services": 2,
                "percentage": 60.0
            },
            "alibaba": {
                "hourly": round(hourly_spend * 0.4, 2),
                "monthly": round(hourly_spend * 0.4 * 24 * 30, 2),
                "services": 1,
                "percentage": 40.0
            }
        },
        "predicted_savings": {
            "total": round(random.uniform(0.15, 0.25), 2),
            "monthly_projection": round(random.uniform(4.5, 7.5), 2)
        },
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/budget-status")
async def get_budget_status():
    return {
        "budget_status": {
            "monthly_budget": 10000.0,
            "current_spend": st.session_state.api_data['current_spend'],
            "utilization_percent": st.session_state.api_data['budget_utilization'],
            "credits_available": 2000.0,
            "budget_remaining": 10000.0 - st.session_state.api_data['current_spend'],
            "alert_threshold": 0.8,
            "is_over_budget": st.session_state.api_data['current_spend'] > 10000.0,
            "needs_alert": st.session_state.api_data['budget_utilization'] > 80.0,
            "regional_discounts": {
                "us-east-1": 0.05,
                "us-west-2": 0.03,
                "eu-west-1": 0.04,
                "ap-southeast-1": 0.06
            }
        },
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.get("/api/policy-stats")
async def get_policy_stats():
    return {
        "policy_stats": {
            "total_decisions": st.session_state.api_data['decisions_count'],
            "auto_approved": st.session_state.api_data['auto_approved'],
            "escalated": st.session_state.api_data['escalated'],
            "pending": 0,
            "rejected": 0
        },
        "recent_decisions": [
            {
                "timestamp": datetime.now().isoformat(),
                "service": random.choice(["service1", "service2", "service3"]),
                "policy_status": random.choice(["auto_approved", "escalated"]),
                "reasoning": "All policy criteria met",
                "cost_delta_percent": round(random.uniform(2, 8), 1),
                "predicted_savings": round(random.uniform(0.05, 0.15), 2),
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "policy_violations": [],
                "budget_impact": round(random.uniform(-0.1, 0.1), 2),
                "credit_utilization": round(random.uniform(0, 0.05), 2)
            }
        ],
        "timestamp": datetime.now().isoformat() + "Z"
    }

@app.post("/api/simulate-price-spike")
async def simulate_price_spike(spike_data: dict):
    provider = spike_data.get('provider', 'aws')
    spike_percentage = spike_data.get('spike_percentage', 50)
    
    return {
        "status": "price_spike_simulated",
        "provider": provider,
        "spike_percentage": spike_percentage,
        "ai_response": "Re-evaluating optimal routing for all services...",
        "estimated_impact": f"Expected {spike_percentage}% cost increase for {provider} services",
        "timestamp": datetime.now().isoformat() + "Z"
    }

# Start FastAPI server in background
def start_api_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps API Backend",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 SWEN AIOps API Backend")
st.markdown("**Status:** API service running with dynamic mock data")

# Start API server if not already running
if 'api_server_started' not in st.session_state:
    st.session_state.api_server_started = True
    # Start FastAPI server in background thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    time.sleep(2)  # Give server time to start

# Auto-display mock data
st.subheader("📊 Live Mock Data")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Services", "3")
    st.metric("Providers", "2")
    st.metric("Total Cost/hr", f"${random.uniform(1.2, 1.8):.2f}")

with col2:
    st.metric("AI Decisions", st.session_state.api_data['decisions_count'])
    st.metric("Auto-Approved", st.session_state.api_data['auto_approved'])
    st.metric("Escalated", st.session_state.api_data['escalated'])

with col3:
    st.metric("Budget Utilization", f"{st.session_state.api_data['budget_utilization']:.1f}%")
    st.metric("Credits Available", "$2,000")
    st.metric("Savings Potential", f"${random.uniform(0.15, 0.25):.2f}/hr")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 API Endpoints")
    st.code("""
    GET /healthz - Health check
    GET /api/telemetry - Telemetry data
    GET /api/decisions - AI decisions
    GET /api/metrics - System metrics
    GET /api/cost-analysis - Cost analysis
    GET /api/policy-visibility - Policy visibility
    GET /api/gitops-history - GitOps history
    GET /api/economics-view - Economics view
    GET /api/budget-status - Budget status
    GET /api/policy-stats - Policy statistics
    POST /api/simulate-price-spike - Price spike simulation
    """)

with col2:
    st.subheader("🔗 Connection Info")
    st.info("""
    **API URL:** `https://swen-ai-ops-api.streamlit.app`
    **Status:** Running (Simulated)
    **Mode:** Mock Data
    """)

# Test endpoints
st.subheader("🧪 Test Endpoints")

if st.button("Test Health Check"):
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            st.success("✅ Health check passed!")
            st.json(response.json())
        else:
            st.error(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test Telemetry"):
    try:
        response = requests.get("http://localhost:8000/api/telemetry", timeout=5)
        if response.status_code == 200:
            st.success("✅ Telemetry endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ Telemetry failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test AI Decisions"):
    try:
        response = requests.get("http://localhost:8000/api/decisions", timeout=5)
        if response.status_code == 200:
            st.success("✅ AI decisions endpoint working!")
            data = response.json()
            st.json(data)
            st.info(f"Total decisions: {data.get('total', 0)}")
        else:
            st.error(f"❌ Decisions failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test Policy Visibility"):
    try:
        response = requests.get("http://localhost:8000/api/policy-visibility", timeout=5)
        if response.status_code == 200:
            st.success("✅ Policy visibility endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ Policy visibility failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test GitOps History"):
    try:
        response = requests.get("http://localhost:8000/api/gitops-history", timeout=5)
        if response.status_code == 200:
            st.success("✅ GitOps history endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ GitOps history failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test Economics View"):
    try:
        response = requests.get("http://localhost:8000/api/economics-view", timeout=5)
        if response.status_code == 200:
            st.success("✅ Economics view endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ Economics view failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test Budget Status"):
    try:
        response = requests.get("http://localhost:8000/api/budget-status", timeout=5)
        if response.status_code == 200:
            st.success("✅ Budget status endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ Budget status failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.button("Test Policy Stats"):
    try:
        response = requests.get("http://localhost:8000/api/policy-stats", timeout=5)
        if response.status_code == 200:
            st.success("✅ Policy stats endpoint working!")
            st.json(response.json())
        else:
            st.error(f"❌ Policy stats failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

# Live data display
st.subheader("📊 Live Data Preview")

# Show sample data prominently
st.markdown("### 🔍 Sample API Responses")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Telemetry", "Decisions", "Health", "Policy", "GitOps", "Economics", "Budget"])

with tab1:
    st.markdown("**GET /api/telemetry**")
    try:
        response = requests.get("http://localhost:8000/api/telemetry", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab2:
    st.markdown("**GET /api/decisions**")
    try:
        response = requests.get("http://localhost:8000/api/decisions", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab3:
    st.markdown("**GET /healthz**")
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab4:
    st.markdown("**GET /api/policy-visibility**")
    try:
        response = requests.get("http://localhost:8000/api/policy-visibility", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab5:
    st.markdown("**GET /api/gitops-history**")
    try:
        response = requests.get("http://localhost:8000/api/gitops-history", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab6:
    st.markdown("**GET /api/economics-view**")
    try:
        response = requests.get("http://localhost:8000/api/economics-view", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab7:
    st.markdown("**GET /api/budget-status**")
    try:
        response = requests.get("http://localhost:8000/api/budget-status", timeout=5)
        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# Keep the app running
st.markdown("---")
st.markdown("**Note:** This app runs a FastAPI server on port 8000 with dynamic mock data. The dashboard can connect to this URL for live data.")
