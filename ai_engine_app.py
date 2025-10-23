#!/usr/bin/env python3
"""
SWEN AIOps AI Engine - Streamlit App
AI decision engine running as Streamlit app
"""

import streamlit as st
import json
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps AI Engine",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SWEN AIOps AI Engine")
st.markdown("**Status:** AI decision engine simulation")

# Mock AI Engine functions
def generate_telemetry():
    """Generate mock telemetry data"""
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
        }
    }

def generate_ai_decision():
    """Generate mock AI decision"""
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
    
    return {
        "timestamp": datetime.now().isoformat() + "Z",
        "service": service,
        "action": "move",
        "from_provider": from_provider,
        "to_provider": to_provider,
        "reason": random.choice(reasons),
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "estimated_savings": round(random.uniform(0.05, 0.15), 2),
        "git_branch": f"ai-recommendation/{service}-{int(datetime.now().timestamp())}",
        "commit_sha": f"{random.randint(100000, 999999):06x}"
    }

# Initialize session state
if 'telemetry_data' not in st.session_state:
    st.session_state.telemetry_data = generate_telemetry()

if 'decisions_history' not in st.session_state:
    st.session_state.decisions_history = []

if 'engine_running' not in st.session_state:
    st.session_state.engine_running = False

# Control panel
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 AI Engine Control")
    if st.button("Start AI Engine", disabled=st.session_state.engine_running):
        st.session_state.engine_running = True
        st.success("✅ AI Engine started!")

with col2:
    st.subheader("📊 Telemetry Simulator")
    if st.button("Generate New Telemetry"):
        st.session_state.telemetry_data = generate_telemetry()
        st.success("✅ New telemetry generated!")

# Status display
st.subheader("📈 System Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.engine_running:
        st.success("🤖 AI Engine: Running")
    else:
        st.warning("🤖 AI Engine: Stopped")

with status_col2:
    st.success("📊 Simulator: Active")

with status_col3:
    st.success("📄 Telemetry: Available")

# AI Decision making
if st.session_state.engine_running:
    st.subheader("🧠 AI Decision Making")
    
    if st.button("Make AI Decision"):
        decision = generate_ai_decision()
        st.session_state.decisions_history.append(decision)
        st.success(f"✅ AI Decision made for {decision['service']}!")
        
        # Display the decision
        with st.expander("Latest Decision Details", expanded=True):
            st.write(f"**Service:** {decision['service']}")
            st.write(f"**Action:** Move from {decision['from_provider']} to {decision['to_provider']}")
            st.write(f"**Reason:** {decision['reason']}")
            st.write(f"**Confidence:** {decision['confidence']:.2f}")
            st.write(f"**Estimated Savings:** ${decision['estimated_savings']:.2f}/hr")
            st.write(f"**Git Branch:** {decision['git_branch']}")

# Live telemetry display
st.subheader("📊 Live Telemetry Data")

for service, data in st.session_state.telemetry_data.items():
    with st.expander(f"Service: {service}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Current Provider:** {data.get('current_provider', 'Unknown')}")
            if 'aws' in data:
                st.write("**AWS Metrics:**")
                st.json(data['aws'])
        
        with col2:
            if 'alibaba' in data:
                st.write("**Alibaba Cloud Metrics:**")
                st.json(data['alibaba'])

# AI Decisions History
st.subheader("🧠 AI Decisions History")

if st.session_state.decisions_history:
    for i, decision in enumerate(reversed(st.session_state.decisions_history[-5:])):  # Show last 5 decisions
        with st.expander(f"Decision {len(st.session_state.decisions_history) - i}: {decision.get('service', 'Unknown')} - {decision.get('timestamp', 'Unknown time')[:19]}"):
            st.write(f"**Action:** {decision.get('action', 'Unknown')}")
            st.write(f"**From:** {decision.get('from_provider', 'Unknown')}")
            st.write(f"**To:** {decision.get('to_provider', 'Unknown')}")
            st.write(f"**Reason:** {decision.get('reason', 'No reason provided')}")
            st.write(f"**Confidence:** {decision.get('confidence', 0):.2f}")
else:
    st.info("No AI decisions yet. Start the AI Engine and make decisions!")

# Auto-refresh
if st.session_state.engine_running:
    import time
    time.sleep(5)
    st.rerun()

st.markdown("---")
st.markdown("**Note:** This app simulates the AI Engine and Telemetry Simulator. Keep this tab open for continuous operation.")
