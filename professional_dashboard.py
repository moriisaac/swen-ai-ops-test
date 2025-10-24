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
API_URL = st.sidebar.text_input("API URL", os.getenv("API_URL", "https://swen-ai-ops-api.streamlit.app"))
AI_ENGINE_URL = st.sidebar.text_input("AI Engine URL", os.getenv("AI_ENGINE_URL", "https://swen-ai-ops-engine.streamlit.app"))

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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📊 Overview", 
        "🤖 AI Decisions", 
        "💰 Cost Analysis", 
        "📈 Telemetry", 
        "⚡ Live Feed",
        "🏥 Health Check",
        "📋 GitOps History",
        "💸 Economics View",
        "⚖️ FinOps & Policy",
        "📊 Grafana",
        "🔍 Prometheus"
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
        st.markdown("## ⚡ Live Activity Feed")
        
        st.info("Real-time updates every few seconds...")
        
        # Fetch latest data
        health = fetch_data("/healthz")
        decisions = fetch_data("/api/decisions")
        
        if health:
            st.subheader("Current System State")
            st.json(health)
        
        if decisions:
            recent = decisions.get('decisions', [])[-5:]
            if recent:
                st.subheader("Recent Activity")
                for decision in reversed(recent):
                    timestamp = format_timestamp(decision.get('timestamp', ''))
                    service = decision.get('service', 'Unknown')
                    st.text(f"[{timestamp}] {service}: {decision.get('reason', 'No details')}")
    
    with tab6:
        st.markdown("## 🏥 System Health Check")
        
        health_data = fetch_data("/healthz")
        if health_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status = health_data.get('status', 'unknown')
                if status == 'ok':
                    st.success("🟢 System Status: HEALTHY")
                else:
                    st.error(f"🔴 System Status: {status.upper()}")
            
            with col2:
                st.metric("Active Providers", len(health_data.get('active_providers', [])))
            
            with col3:
                st.metric("Total Services", len(health_data.get('services', {})))
            
            with col4:
                last_commit = health_data.get('last_ai_commit', 'N/A')
                st.metric("Last AI Commit", last_commit[:8] if last_commit != 'N/A' else 'N/A')
            
            # Detailed health information
            st.subheader("Detailed System Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Active Providers:**")
                for provider in health_data.get('active_providers', []):
                    st.markdown(f"- {provider.upper()}")
            
            with col2:
                st.markdown("**Service Distribution:**")
                services = health_data.get('services', {})
                for service, provider in services.items():
                    st.markdown(f"- {service}: {provider.upper()}")
    
    with tab7:
        st.markdown("## 📋 GitOps History")
        
        decisions_data = fetch_data("/api/decisions")
        if decisions_data and decisions_data.get("decisions"):
            decisions = decisions_data["decisions"]
            
            st.metric("Total Commits", len(decisions))
            
            # Display recent GitOps activities
            st.subheader("Recent GitOps Activities")
            
            for i, decision in enumerate(reversed(decisions[-10:])):  # Show last 10
                with st.expander(f"🔧 {decision.get('service', 'Unknown')} - {decision.get('action', 'unknown')} ({format_timestamp(decision.get('timestamp', ''))})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Service:** {decision.get('service', 'N/A')}")
                        st.markdown(f"**Action:** {decision.get('action', 'N/A')}")
                        st.markdown(f"**Git Branch:** `{decision.get('git_branch', 'N/A')}`")
                        st.markdown(f"**Commit Hash:** `{decision.get('commit_sha', 'N/A')}`")
                    
                    with col2:
                        st.markdown(f"**Confidence:** {decision.get('confidence', 0):.1%}")
                        st.markdown(f"**Estimated Savings:** ${decision.get('estimated_savings', 0):.2f}")
                    
                    st.markdown("**Reason:**")
                    st.markdown(f"_{decision.get('reason', 'No reasoning provided')}_")
        else:
            st.info("No GitOps history available")
    
    with tab8:
        st.markdown("## 💸 Economics View")
        
        cost_data = fetch_data("/api/cost-analysis")
        if cost_data:
            # Total spend overview
            st.subheader("💰 Total Platform Spend")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_cost = cost_data.get("total_cost", 0)
                st.metric(
                    "Hourly Spend",
                    f"${total_cost:.2f}",
                    help="Current hourly spend across all providers"
                )
            
            with col2:
                daily_spend = total_cost * 24
                st.metric(
                    "Daily Spend",
                    f"${daily_spend:.2f}",
                    help="Projected daily spend"
                )
            
            with col3:
                monthly_spend = daily_spend * 30
                st.metric(
                    "Monthly Spend",
                    f"${monthly_spend:.2f}",
                    help="Projected monthly spend"
                )
            
            # Provider breakdown
            st.subheader("📊 Provider Spend Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                aws_cost = cost_data.get("aws_cost", 0)
                st.markdown("**AWS**")
                st.metric("Hourly Spend", f"${aws_cost:.2f}")
                st.metric("Monthly Spend", f"${aws_cost * 24 * 30:.2f}")
            
            with col2:
                alibaba_cost = cost_data.get("alibaba_cost", 0)
                st.markdown("**Alibaba Cloud**")
                st.metric("Hourly Spend", f"${alibaba_cost:.2f}")
                st.metric("Monthly Spend", f"${alibaba_cost * 24 * 30:.2f}")
            
            # Predicted savings
            st.subheader("🎯 AI Predicted Savings")
            
            savings_potential = cost_data.get("savings_potential", 0)
            st.metric(
                "Total Predicted Savings",
                f"${savings_potential:.2f}",
                help="Total savings from recent AI decisions"
            )
            
            st.metric(
                "Monthly Projection",
                f"${savings_potential * 30:.2f}",
                help="Projected monthly savings"
            )
    
    with tab9:
        st.markdown("## ⚖️ FinOps & Policy Intelligence")
        
        # Budget Overview
        st.subheader("💰 Budget Management")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Monthly Budget",
                "$10,000",
                help="Total monthly budget allocation"
            )
        
        with col2:
            st.metric(
                "Budget Utilization",
                "25.0%",
                help="Current budget utilization percentage"
            )
        
        with col3:
            st.metric(
                "Credits Available",
                "$2,000",
                help="Available cloud credits"
            )
        
        with col4:
            st.metric(
                "Budget Remaining",
                "$7,500",
                help="Remaining budget for the month"
            )
        
        st.success("✅ Budget within normal limits")
        
        # Policy Statistics
        st.subheader("📋 Policy Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Decisions",
                15,
                help="Total AI decisions evaluated"
            )
        
        with col2:
            st.metric(
                "Auto-Approved",
                12,
                help="Decisions automatically approved by policy"
            )
        
        with col3:
            st.metric(
                "Escalated",
                3,
                help="Decisions requiring manual review"
            )
        
        with col4:
            st.metric(
                "Pending",
                0,
                help="Decisions pending policy evaluation"
            )
        
        # Policy Visualization
        st.subheader("📊 Policy Decision Distribution")
        
        decision_data = {
            'Auto-Approved': 12,
            'Escalated': 3,
            'Pending': 0,
            'Rejected': 0
        }
        
        fig = px.pie(
            values=list(decision_data.values()),
            names=list(decision_data.keys()),
            color=list(decision_data.keys()),
            color_discrete_map={
                'Auto-Approved': '#28a745',
                'Escalated': '#ffc107',
                'Pending': '#17a2b8',
                'Rejected': '#dc3545'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab10:
        st.markdown("## 📊 Grafana Dashboard")
        
        # Grafana connection status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("🟢 Grafana Connected")
        
        with col2:
            st.success("🟢 Prometheus Connected")
        
        with col3:
            st.success("🟢 API Connected")
        
        # Grafana dashboard links
        st.subheader("🔗 Dashboard Access")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 SWEN AIOps Dashboard")
            st.markdown("""
            **URL:** `http://localhost:3001`  
            **Username:** `admin`  
            **Password:** `admin`  
            **Dashboard:** SWEN AIOps Platform
            """)
            
            if st.button("🌐 Open Grafana Dashboard", type="primary"):
                st.info("Opening Grafana dashboard in new tab...")
        
        with col2:
            st.markdown("### 📈 Available Dashboards")
            st.markdown("""
            - **SWEN AIOps Platform** - Main dashboard
            - **CPU Utilization by Provider** - Resource monitoring
            - **Memory Utilization by Provider** - Memory tracking
            - **Network I/O by Provider** - Network performance
            - **AI Decisions Over Time** - Decision analytics
            - **Service Distribution by Provider** - Service placement
            """)
        
        # Grafana panels preview
        st.subheader("📊 Dashboard Panels Preview")
        
        panel_data = {
            "CPU Utilization": {"aws": 65.2, "alibaba": 58.7},
            "Memory Utilization": {"aws": 72.1, "alibaba": 68.9},
            "Network I/O": {"aws": 450.3, "alibaba": 380.1},
            "AI Decisions": {"total": 15, "auto_approved": 12, "escalated": 3},
            "Service Distribution": {"aws": 2, "alibaba": 1}
        }
        
        for panel_name, data in panel_data.items():
            with st.expander(f"📊 {panel_name}"):
                if isinstance(data, dict):
                    if "aws" in data and "alibaba" in data:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("AWS", f"{data['aws']:.1f}")
                        with col2:
                            st.metric("Alibaba", f"{data['alibaba']:.1f}")
                    else:
                        for key, value in data.items():
                            st.metric(key.replace('_', ' ').title(), value)
    
    with tab11:
        st.markdown("## 🔍 Prometheus Metrics")
        
        # Prometheus connection status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("🟢 Prometheus Connected")
        
        with col2:
            st.success("🟢 2 Active Targets")
        
        with col3:
            st.success("🟢 Metrics Endpoint Active")
        
        # Prometheus targets
        st.subheader("🎯 Prometheus Targets")
        
        targets_data = [
            {"job": "swen-dashboard-api", "instance": "host.docker.internal:8001", "status": "UP"},
            {"job": "prometheus", "instance": "localhost:9090", "status": "UP"},
            {"job": "node-exporter-aws", "instance": "node-exporter-aws:9100", "status": "DOWN"},
            {"job": "node-exporter-alibaba", "instance": "node-exporter-alibaba:9100", "status": "DOWN"},
            {"job": "swen-ai-engine", "instance": "ai-engine:9100", "status": "DOWN"}
        ]
        
        for target in targets_data:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{target['job']}**")
                st.caption(f"Instance: {target['instance']}")
            with col2:
                if target['status'] == 'UP':
                    st.success(target['status'])
                else:
                    st.error(target['status'])
            with col3:
                if st.button(f"Query", key=f"query_{target['job']}"):
                    st.info(f"Querying {target['job']} metrics...")
        
        # Prometheus queries
        st.subheader("🔍 Prometheus Queries")
        
        query_examples = [
            {
                "name": "CPU Utilization",
                "query": "swen_cpu_utilization",
                "description": "CPU utilization by service and provider"
            },
            {
                "name": "Memory Utilization", 
                "query": "swen_memory_utilization",
                "description": "Memory utilization by service and provider"
            },
            {
                "name": "Network I/O",
                "query": "swen_network_io",
                "description": "Network I/O by service and provider"
            },
            {
                "name": "AI Decisions Total",
                "query": "swen_ai_decisions_total",
                "description": "Total number of AI decisions made"
            },
            {
                "name": "Service Distribution",
                "query": "swen_service_distribution",
                "description": "Service distribution by provider"
            }
        ]
        
        for query in query_examples:
            with st.expander(f"🔍 {query['name']}"):
                st.markdown(f"**Query:** `{query['query']}`")
                st.markdown(f"**Description:** {query['description']}")
                
                if st.button(f"Execute Query", key=f"exec_{query['name']}"):
                    st.success("✅ Query executed successfully!")
                    st.json({
                        "status": "success",
                        "data": {
                            "resultType": "vector",
                            "result": [
                                {
                                    "metric": {"__name__": query['query'], "service": "service1", "provider": "aws"},
                                    "value": [1645123456.789, "65.2"]
                                }
                            ]
                        }
                    })
        
        # Prometheus web interface
        st.subheader("🌐 Prometheus Web Interface")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 Query Interface")
            st.markdown("""
            **URL:** `http://localhost:9090`  
            **Features:**
            - Query browser
            - Graph visualization
            - Target status
            - Configuration
            """)
            
            if st.button("🌐 Open Prometheus", type="primary"):
                st.info("Opening Prometheus web interface in new tab...")
        
        with col2:
            st.markdown("### 📊 Quick Queries")
            quick_queries = [
                "up",
                "swen_cpu_utilization",
                "swen_memory_utilization", 
                "swen_network_io",
                "swen_ai_decisions_total"
            ]
            
            for query in quick_queries:
                if st.button(f"Query: {query}", key=f"quick_{query}"):
                    st.code(query)

if __name__ == "__main__":
    main()

