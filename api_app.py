#!/usr/bin/env python3
"""
SWEN AIOps API Backend - Streamlit App
FastAPI backend service running as Streamlit app
"""

import streamlit as st
import uvicorn
import threading
import time
from dashboard.api.main import app as fastapi_app

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps API Backend",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 SWEN AIOps API Backend")
st.markdown("**Status:** Running FastAPI backend service")

# Start FastAPI server in background
def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8001, log_level="info")

# Check if server is already running
if not hasattr(st.session_state, 'api_running'):
    st.session_state.api_running = False

if not st.session_state.api_running:
    st.info("Starting FastAPI server...")
    # Start server in background thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    st.session_state.api_running = True
    time.sleep(2)  # Give server time to start

if st.session_state.api_running:
    st.success("✅ FastAPI server is running!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 API Endpoints")
        st.code("""
        GET /healthz - Health check
        GET /api/telemetry - Telemetry data
        GET /api/decisions - AI decisions
        GET /api/cost-analysis - Cost analysis
        GET /metrics - Prometheus metrics
        """)
    
    with col2:
        st.subheader("🔗 Connection Info")
        st.info(f"""
        **API URL:** `{st.session_state.get('api_url', 'http://localhost:8001')}`
        **Status:** Running
        **Port:** 8001
        """)
    
    # Test endpoints
    st.subheader("🧪 Test Endpoints")
    
    if st.button("Test Health Check"):
        try:
            import requests
            response = requests.get("http://localhost:8001/healthz", timeout=5)
            if response.status_code == 200:
                st.success("✅ Health check passed!")
                st.json(response.json())
            else:
                st.error(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
    
    if st.button("Test Telemetry"):
        try:
            import requests
            response = requests.get("http://localhost:8001/api/telemetry", timeout=5)
            if response.status_code == 200:
                st.success("✅ Telemetry endpoint working!")
                st.json(response.json())
            else:
                st.error(f"❌ Telemetry failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")

# Keep the app running
st.markdown("---")
st.markdown("**Note:** This app runs the FastAPI backend service. Keep this tab open for the API to remain active.")
