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
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps API Backend",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 SWEN AIOps API Backend")
st.markdown("**Status:** API service simulation")

# Mock API data
def get_mock_telemetry():
    return {
        "service1": {
            "current_provider": "aws",
            "aws": {
                "cost": 0.45,
                "latency": 12.5,
                "credits": 0.85,
                "available_gpus": 8,
                "cpu_utilization": 65.2,
                "memory_utilization": 72.1,
                "network_io": 450.3,
                "region": "us-east-1",
                "instance": "m5.large"
            },
            "alibaba": {
                "cost": 0.38,
                "latency": 15.2,
                "credits": 0.92,
                "available_gpus": 6,
                "cpu_utilization": 58.7,
                "memory_utilization": 68.9,
                "network_io": 380.1,
                "region": "ap-southeast-1",
                "instance": "ecs.c5.large"
            }
        },
        "service2": {
            "current_provider": "alibaba",
            "aws": {
                "cost": 0.52,
                "latency": 18.3,
                "credits": 0.78,
                "available_gpus": 4,
                "cpu_utilization": 71.5,
                "memory_utilization": 75.8,
                "network_io": 520.7,
                "region": "us-west-2",
                "instance": "m5.xlarge"
            },
            "alibaba": {
                "cost": 0.41,
                "latency": 14.7,
                "credits": 0.88,
                "available_gpus": 7,
                "cpu_utilization": 62.3,
                "memory_utilization": 69.4,
                "network_io": 410.2,
                "region": "ap-northeast-1",
                "instance": "ecs.c6.large"
            }
        }
    }

def get_mock_decisions():
    return {
        "decisions": [
            {
                "timestamp": datetime.now().isoformat() + "Z",
                "service": "service1",
                "action": "move",
                "from_provider": "alibaba",
                "to_provider": "aws",
                "reason": "Cost optimization: AWS offers 18% lower cost with similar performance",
                "confidence": 0.87,
                "estimated_savings": 0.07,
                "git_branch": "ai-recommendation/service1-1761226530",
                "commit_sha": "a1b2c3d4e5f6"
            }
        ]
    }

def get_mock_health():
    return {
        "status": "ok",
        "active_providers": ["aws", "alibaba"],
        "services": {"service1": "aws", "service2": "alibaba"},
        "timestamp": datetime.now().isoformat() + "Z"
    }

# Display API status
st.success("✅ API service is running!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 API Endpoints")
    st.code("""
    GET /healthz - Health check
    GET /api/telemetry - Telemetry data
    GET /api/decisions - AI decisions
    GET /api/cost-analysis - Cost analysis
    """)

with col2:
    st.subheader("🔗 Connection Info")
    st.info("""
    **API URL:** `https://swen-aiops-api.streamlit.app`
    **Status:** Running (Simulated)
    **Mode:** Mock Data
    """)

# Test endpoints
st.subheader("🧪 Test Endpoints")

if st.button("Test Health Check"):
    health_data = get_mock_health()
    st.success("✅ Health check passed!")
    st.json(health_data)

if st.button("Test Telemetry"):
    telemetry_data = get_mock_telemetry()
    st.success("✅ Telemetry endpoint working!")
    st.json(telemetry_data)

if st.button("Test AI Decisions"):
    decisions_data = get_mock_decisions()
    st.success("✅ AI decisions endpoint working!")
    st.json(decisions_data)

# Live data display
st.subheader("📊 Live Data Preview")

tab1, tab2, tab3 = st.tabs(["Telemetry", "Decisions", "Health"])

with tab1:
    st.json(get_mock_telemetry())

with tab2:
    st.json(get_mock_decisions())

with tab3:
    st.json(get_mock_health())

# Keep the app running
st.markdown("---")
st.markdown("**Note:** This app simulates the API backend service. The dashboard can connect to this URL for live data.")
