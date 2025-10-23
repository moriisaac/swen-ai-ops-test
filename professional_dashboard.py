#!/usr/bin/env python3
"""
SWEN AIOps Professional Dashboard
Modern, professional interface for monitoring AI-driven infrastructure decisions
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import os

# Page configuration
st.set_page_config(
    page_title="SWEN AIOps Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    
    .provider-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .aws-card { border-left-color: #FF9900; }
    .alibaba-card { border-left-color: #FF6A00; }
    
    .decision-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = st.sidebar.text_input("API URL", os.getenv("API_URL", "https://swen-aiops-api.streamlit.app"))
AI_ENGINE_URL = st.sidebar.text_input("AI Engine URL", os.getenv("AI_ENGINE_URL", "https://swen-aiops-engine.streamlit.app"))

# Helper functions
@st.cache_data(ttl=10)
def fetch_data(endpoint: str):
    """Fetch data from API with caching."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return get_mock_data(endpoint)

def get_mock_data(endpoint: str):
    """Generate professional mock data."""
    if endpoint == "/api/telemetry":
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
            },
            "service3": {
                "current_provider": "aws",
                "aws": {
                    "cost": 0.38,
                    "latency": 11.8,
                    "credits": 0.91,
                    "available_gpus": 9,
                    "cpu_utilization": 58.9,
                    "memory_utilization": 64.2,
                    "network_io": 380.5,
                    "region": "eu-west-1",
                    "instance": "m5.large"
                },
                "alibaba": {
                    "cost": 0.35,
                    "latency": 16.1,
                    "credits": 0.95,
                    "available_gpus": 5,
                    "cpu_utilization": 55.6,
                    "memory_utilization": 61.8,
                    "network_io": 350.8,
                    "region": "ap-south-1",
                    "instance": "ecs.c5.xlarge"
                }
            }
        }
    elif endpoint == "/api/decisions":
        return {
            "decisions": [
                {
                    "timestamp": "2025-10-23T13:45:30Z",
                    "service": "service1",
                    "action": "move",
                    "from_provider": "alibaba",
                    "to_provider": "aws",
                    "reason": "Cost optimization: AWS offers 18% lower cost with similar performance",
                    "confidence": 0.87,
                    "estimated_savings": 0.07,
                    "git_branch": "ai-recommendation/service1-1761226530",
                    "commit_sha": "a1b2c3d4e5f6"
                },
                {
                    "timestamp": "2025-10-23T13:30:15Z",
                    "service": "service2",
                    "action": "move",
                    "from_provider": "aws",
                    "to_provider": "alibaba",
                    "reason": "Performance optimization: Alibaba Cloud shows 22% better latency",
                    "confidence": 0.92,
                    "estimated_savings": 0.11,
                    "git_branch": "ai-recommendation/service2-1761225415",
                    "commit_sha": "b2c3d4e5f6g7"
                }
            ]
        }
    elif endpoint == "/api/cost-analysis":
        return {
            "total_cost": 1.35,
            "aws_cost": 0.83,
            "alibaba_cost": 0.52,
            "savings_potential": 0.18,
            "trend": "decreasing"
        }
    elif endpoint == "/healthz":
        return {
            "status": "ok",
            "active_providers": ["aws", "alibaba"],
            "services": {"service1": "aws", "service2": "alibaba", "service3": "aws"},
            "timestamp": "2025-10-23T13:46:56Z"
        }
    return None

def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return ts

# Main dashboard
def main():
    # Professional header
    st.markdown('<div class="main-header">🧠 SWEN AIOps Platform</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Intelligent Infrastructure Management & Cost Optimization</p>', unsafe_allow_html=True)
    
    # Sidebar with professional styling
    with st.sidebar:
        st.markdown("## 🔧 System Control")
        
        # Service status indicators
        st.markdown("### 📊 Service Status")
        
        # Check API connection
        try:
            health_data = fetch_data("/healthz")
            if health_data and health_data.get("status") == "ok":
                st.markdown('<span class="status-indicator status-online"></span> **API Service**', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-indicator status-warning"></span> **API Service (Demo)**', unsafe_allow_html=True)
        except:
            st.markdown('<span class="status-indicator status-warning"></span> **API Service (Demo)**', unsafe_allow_html=True)
        
        # Check AI Engine connection
        try:
            response = requests.get(f"{AI_ENGINE_URL}", timeout=3)
            if response.status_code == 200:
                st.markdown('<span class="status-indicator status-online"></span> **AI Engine**', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-indicator status-warning"></span> **AI Engine (Demo)**', unsafe_allow_html=True)
        except:
            st.markdown('<span class="status-indicator status-warning"></span> **AI Engine (Demo)**', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Refresh controls
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🤖 AI Decisions", 
        "💰 Cost Analysis", 
        "📈 Telemetry", 
        "⚙️ System Health"
    ])
    
    with tab1:
        st.markdown("## 📊 Platform Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card"><h3>Total Services</h3><h1>3</h1></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card"><h3>Active Providers</h3><h1>2</h1></div>', unsafe_allow_html=True)
        
        with col3:
            cost_data = fetch_data("/api/cost-analysis")
            total_cost = cost_data.get("total_cost", 0) if cost_data else 0
            st.markdown(f'<div class="metric-card"><h3>Total Cost/hr</h3><h1>${total_cost:.2f}</h1></div>', unsafe_allow_html=True)
        
        with col4:
            savings = cost_data.get("savings_potential", 0) if cost_data else 0
            st.markdown(f'<div class="metric-card"><h3>Savings Potential</h3><h1>${savings:.2f}</h1></div>', unsafe_allow_html=True)
        
        # Service distribution chart
        st.markdown("## 🏗️ Service Distribution")
        
        telemetry_data = fetch_data("/api/telemetry")
        if telemetry_data:
            service_data = []
            for service, data in telemetry_data.items():
                service_data.append({
                    'Service': service,
                    'Provider': data.get('current_provider', 'unknown').upper(),
                    'Cost': data.get(data.get('current_provider', 'aws'), {}).get('cost', 0)
                })
            
            df = pd.DataFrame(service_data)
            
            # Provider distribution pie chart
            fig = px.pie(df, values='Cost', names='Provider', 
                        title="Cost Distribution by Provider",
                        color_discrete_map={'AWS': '#FF9900', 'ALIBABA': '#FF6A00'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("## 🤖 AI Decision History")
        
        decisions_data = fetch_data("/api/decisions")
        if decisions_data and decisions_data.get("decisions"):
            decisions = decisions_data["decisions"]
            
            for i, decision in enumerate(decisions):
                with st.expander(f"Decision #{len(decisions)-i}: {decision.get('service', 'Unknown')} - {format_timestamp(decision.get('timestamp', ''))}", expanded=(i==0)):
                    st.markdown(f'<div class="decision-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Service:** {decision.get('service', 'Unknown')}")
                        st.write(f"**Action:** Move from {decision.get('from_provider', 'Unknown')} to {decision.get('to_provider', 'Unknown')}")
                        st.write(f"**Confidence:** {decision.get('confidence', 0):.2f}")
                    
                    with col2:
                        st.write(f"**Estimated Savings:** ${decision.get('estimated_savings', 0):.2f}/hr")
                        st.write(f"**Git Branch:** `{decision.get('git_branch', 'N/A')}`")
                        st.write(f"**Commit:** `{decision.get('commit_sha', 'N/A')}`")
                    
                    st.write(f"**Reason:** {decision.get('reason', 'No reason provided')}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No AI decisions available. Start the AI Engine to begin making decisions.")
    
    with tab3:
        st.markdown("## 💰 Cost Analysis")
        
        cost_data = fetch_data("/api/cost-analysis")
        if cost_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💵 Current Costs")
                
                aws_cost = cost_data.get("aws_cost", 0)
                alibaba_cost = cost_data.get("alibaba_cost", 0)
                total_cost = cost_data.get("total_cost", 0)
                
                # Cost breakdown chart
                fig = go.Figure(data=[
                    go.Bar(name='AWS', x=['AWS'], y=[aws_cost], marker_color='#FF9900'),
                    go.Bar(name='Alibaba Cloud', x=['Alibaba'], y=[alibaba_cost], marker_color='#FF6A00')
                ])
                fig.update_layout(title="Cost Breakdown by Provider", yaxis_title="Cost ($/hr)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Savings Analysis")
                
                savings_potential = cost_data.get("savings_potential", 0)
                trend = cost_data.get("trend", "stable")
                
                st.metric("Savings Potential", f"${savings_potential:.2f}/hr", f"{trend}")
                
                # Savings gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = savings_potential * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Savings Potential (%)"},
                    delta = {'reference': 15},
                    gauge = {
                        'axis': {'range': [None, 30]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 10], 'color': "lightgray"},
                            {'range': [10, 20], 'color': "yellow"},
                            {'range': [20, 30], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 25
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("## 📈 Live Telemetry")
        
        telemetry_data = fetch_data("/api/telemetry")
        if telemetry_data:
            for service, data in telemetry_data.items():
                st.markdown(f"### 🖥️ {service.upper()}")
                
                current_provider = data.get('current_provider', 'unknown')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f'<div class="provider-card aws-card">', unsafe_allow_html=True)
                    st.markdown("#### ☁️ AWS Metrics")
                    aws_data = data.get('aws', {})
                    st.metric("Cost", f"${aws_data.get('cost', 0):.2f}/hr")
                    st.metric("Latency", f"{aws_data.get('latency', 0):.1f}ms")
                    st.metric("CPU", f"{aws_data.get('cpu_utilization', 0):.1f}%")
                    st.metric("Memory", f"{aws_data.get('memory_utilization', 0):.1f}%")
                    st.metric("Network I/O", f"{aws_data.get('network_io', 0):.1f} MB/s")
                    st.caption(f"Region: {aws_data.get('region', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="provider-card alibaba-card">', unsafe_allow_html=True)
                    st.markdown("#### 🌏 Alibaba Cloud Metrics")
                    alibaba_data = data.get('alibaba', {})
                    st.metric("Cost", f"${alibaba_data.get('cost', 0):.2f}/hr")
                    st.metric("Latency", f"{alibaba_data.get('latency', 0):.1f}ms")
                    st.metric("CPU", f"{alibaba_data.get('cpu_utilization', 0):.1f}%")
                    st.metric("Memory", f"{alibaba_data.get('memory_utilization', 0):.1f}%")
                    st.metric("Network I/O", f"{alibaba_data.get('network_io', 0):.1f} MB/s")
                    st.caption(f"Region: {alibaba_data.get('region', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
    
    with tab5:
        st.markdown("## ⚙️ System Health")
        
        health_data = fetch_data("/healthz")
        if health_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏥 System Status")
                st.success(f"**Status:** {health_data.get('status', 'Unknown').upper()}")
                st.info(f"**Timestamp:** {format_timestamp(health_data.get('timestamp', ''))}")
                
                st.markdown("### 🌐 Active Providers")
                providers = health_data.get('active_providers', [])
                for provider in providers:
                    st.markdown(f"- {provider.upper()}")
            
            with col2:
                st.markdown("### 🖥️ Service Status")
                services = health_data.get('services', {})
                for service, provider in services.items():
                    st.markdown(f"**{service}:** {provider.upper()}")
        
        # System metrics
        st.markdown("### 📊 Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Uptime", "99.9%", "0.1%")
        
        with col2:
            st.metric("Response Time", "45ms", "-5ms")
        
        with col3:
            st.metric("Throughput", "1.2K req/s", "150")

if __name__ == "__main__":
    main()
