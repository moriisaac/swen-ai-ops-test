#!/usr/bin/env python3
"""
SWEN AIOps AI Engine - Streamlit App
AI decision engine running as Streamlit app
"""

import streamlit as st
import threading
import time
import json
from datetime import datetime
from ai_engine.engine import CostOptimizationEngine
from ai_engine.simulator import TelemetrySimulator

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps AI Engine",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SWEN AIOps AI Engine")
st.markdown("**Status:** Running AI decision engine")

# Initialize components
if not hasattr(st.session_state, 'engine_running'):
    st.session_state.engine_running = False
    st.session_state.simulator_running = False

# Start AI Engine
def run_ai_engine():
    try:
        engine = CostOptimizationEngine()
        engine.run()
    except Exception as e:
        st.error(f"AI Engine error: {e}")

# Start Simulator
def run_simulator():
    try:
        simulator = TelemetrySimulator()
        simulator.run()
    except Exception as e:
        st.error(f"Simulator error: {e}")

# Control panel
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 AI Engine Control")
    if st.button("Start AI Engine", disabled=st.session_state.engine_running):
        engine_thread = threading.Thread(target=run_ai_engine, daemon=True)
        engine_thread.start()
        st.session_state.engine_running = True
        st.success("✅ AI Engine started!")

with col2:
    st.subheader("📊 Telemetry Simulator")
    if st.button("Start Simulator", disabled=st.session_state.simulator_running):
        simulator_thread = threading.Thread(target=run_simulator, daemon=True)
        simulator_thread.start()
        st.session_state.simulator_running = True
        st.success("✅ Simulator started!")

# Status display
st.subheader("📈 System Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    if st.session_state.engine_running:
        st.success("🤖 AI Engine: Running")
    else:
        st.warning("🤖 AI Engine: Stopped")

with status_col2:
    if st.session_state.simulator_running:
        st.success("📊 Simulator: Running")
    else:
        st.warning("📊 Simulator: Stopped")

with status_col3:
    try:
        with open('ai-engine/latest_telemetry.json', 'r') as f:
            telemetry = json.load(f)
        st.success("📄 Telemetry: Available")
    except:
        st.warning("📄 Telemetry: Not available")

# Live telemetry display
st.subheader("📊 Live Telemetry Data")

try:
    with open('ai-engine/latest_telemetry.json', 'r') as f:
        telemetry = json.load(f)
    
    for service, data in telemetry.items():
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

except Exception as e:
    st.error(f"Could not load telemetry: {e}")

# AI Decisions
st.subheader("🧠 Recent AI Decisions")

try:
    with open('ai-engine/decisions.json', 'r') as f:
        decisions = json.load(f)
    
    if decisions:
        for decision in decisions[-3:]:  # Show last 3 decisions
            with st.expander(f"Decision: {decision.get('service', 'Unknown')} - {decision.get('timestamp', 'Unknown time')}"):
                st.write(f"**Action:** {decision.get('action', 'Unknown')}")
                st.write(f"**From:** {decision.get('from_provider', 'Unknown')}")
                st.write(f"**To:** {decision.get('to_provider', 'Unknown')}")
                st.write(f"**Reason:** {decision.get('reason', 'No reason provided')}")
                st.write(f"**Confidence:** {decision.get('confidence', 0):.2f}")
    else:
        st.info("No AI decisions yet. Start the AI Engine to begin making decisions.")
        
except Exception as e:
    st.info("No AI decisions available yet.")

# Auto-refresh
if st.session_state.engine_running or st.session_state.simulator_running:
    time.sleep(5)
    st.rerun()

st.markdown("---")
st.markdown("**Note:** Keep this tab open for the AI Engine and Simulator to remain active.")
