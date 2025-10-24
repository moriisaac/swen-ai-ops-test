#!/usr/bin/env python3
"""
SWEN Cloud Intelligence Console - UI
Real-time dashboard for monitoring AI-driven infrastructure decisions
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Page configuration
st.set_page_config(
    page_title="SWEN Cloud Intelligence Console",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .provider-aws {
        color: #FF9900;
        font-weight: bold;
    }
    .provider-alibaba {
        color: #FF6A00;
        font-weight: bold;
    }
    .status-good {
        color: #28a745;
    }
    .status-warning {
        color: #ffc107;
    }
    .status-critical {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
import os
# Connect to deployed Streamlit apps
API_URL = st.sidebar.text_input("API URL", os.getenv("API_URL", "https://swen-aiops-api.streamlit.app"))
AI_ENGINE_URL = st.sidebar.text_input("AI Engine URL", os.getenv("AI_ENGINE_URL", "https://swen-aiops-engine.streamlit.app"))
REFRESH_INTERVAL = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)

# Helper functions
@st.cache_data(ttl=5)
def fetch_data(endpoint: str):
    """Fetch data from API with caching."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Return mock data for demonstration when API is not available
        return get_mock_data(endpoint)

def get_mock_data(endpoint: str):
    """Generate mock data for demonstration purposes."""
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

def get_provider_color(provider: str) -> str:
    """Get color for provider."""
    colors = {
        'aws': '#FF9900',
        'alibaba': '#FF6A00'
    }
    return colors.get(provider, '#666666')

# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">🧠 SWEN Cloud Intelligence Console</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Connection status indicator
        st.subheader("🔗 Service Status")
        
        # Check API connection
        try:
            health_data = fetch_data("/healthz")
            if health_data and health_data.get("status") == "ok":
                st.success("🟢 API Connected")
            else:
                st.warning("🟡 API Demo Mode")
        except:
            st.warning("🟡 API Demo Mode")
        
        # Check AI Engine connection
        try:
            import requests
            response = requests.get(f"{AI_ENGINE_URL}", timeout=3)
            if response.status_code == 200:
                st.success("🟢 AI Engine Connected")
            else:
                st.warning("🟡 AI Engine Offline")
        except:
            st.warning("🟡 AI Engine Offline")
        
        # Service URLs
        st.markdown("**Service URLs:**")
        st.code(f"API: {API_URL}")
        st.code(f"AI Engine: {AI_ENGINE_URL}")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.header("📊 Quick Stats")
        
        # Fetch health data
        health = fetch_data("/healthz")
        if health:
            st.metric("Status", health.get('status', 'unknown').upper())
            st.metric("Active Providers", len(health.get('active_providers', [])))
            st.metric("Services", len(health.get('services', {})))
    
    # Main content
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
    
    # Tab 1: Overview
    with tab1:
        render_overview()
    
    # Tab 2: AI Decisions
    with tab2:
        render_ai_decisions()
    
    # Tab 3: Cost Analysis
    with tab3:
        render_cost_analysis()
    
    # Tab 4: Telemetry
    with tab4:
        render_telemetry()
    
    # Tab 5: Live Feed
    with tab5:
        render_live_feed()
    
    # Tab 6: Health Check
    with tab6:
        render_health_check()
    
    # Tab 7: GitOps History
    with tab7:
        render_gitops_history()
    
    # Tab 8: Economics View
    with tab8:
        render_economics_view()
    
    # Tab 9: FinOps & Policy
    with tab9:
        render_finops_policy()
    
    # Tab 10: Grafana
    with tab10:
        render_grafana()
    
    # Tab 11: Prometheus
    with tab11:
        render_prometheus()
    
    # Auto-refresh
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

def render_overview():
    """Render overview dashboard."""
    st.header("System Overview")
    
    # Fetch data
    metrics = fetch_data("/api/metrics")
    health = fetch_data("/healthz")
    
    if not metrics or not health:
        st.warning("Unable to fetch system data")
        return
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Services",
            metrics['services']['total'],
            help="Number of managed services"
        )
    
    with col2:
        st.metric(
            "Current Hourly Cost",
            f"${metrics['cost']['current_hourly']:.2f}",
            help="Total cost per hour across all providers"
        )
    
    with col3:
        st.metric(
            "Est. Monthly Cost",
            f"${metrics['cost']['estimated_monthly']:.2f}",
            help="Estimated monthly cost"
        )
    
    with col4:
        st.metric(
            "AI Confidence",
            f"{metrics['ai_decisions']['avg_confidence']:.1%}",
            help="Average confidence of recent AI decisions"
        )
    
    st.markdown("---")
    
    # Service distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Service Distribution by Provider")
        
        provider_data = metrics['services']['by_provider']
        if provider_data:
            fig = px.pie(
                values=list(provider_data.values()),
                names=list(provider_data.keys()),
                color=list(provider_data.keys()),
                color_discrete_map={'aws': '#FF9900', 'alibaba': '#FF6A00'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service data available")
    
    with col2:
        st.subheader("Current Service Placement")
        
        services = health.get('services', {})
        if services:
            df = pd.DataFrame([
                {'Service': k, 'Provider': v} 
                for k, v in services.items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No service data available")
    
    # AI Decision Summary
    st.markdown("---")
    st.subheader("AI Decision Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Decisions",
            metrics['ai_decisions']['total']
        )
    
    with col2:
        st.metric(
            "Recent Decisions",
            metrics['ai_decisions']['recent_count']
        )
    
    with col3:
        st.metric(
            "Predicted Savings",
            f"${metrics['ai_decisions']['total_predicted_savings']:.2f}/mo"
        )

def render_ai_decisions():
    """Render AI decisions tab."""
    st.header("🤖 AI Decision History")
    
    decisions_data = fetch_data("/api/decisions")
    policy_data = fetch_data("/api/policy-visibility")
    
    if not decisions_data:
        st.warning("Unable to fetch AI decisions")
        return
    
    decisions = decisions_data.get('decisions', [])
    
    if not decisions:
        st.info("No AI decisions recorded yet")
        return
    
    # Enhanced metrics with policy visibility
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Decisions", decisions_data.get('total', 0))
    
    with col2:
        if policy_data:
            auto_approved = policy_data.get('policy_stats', {}).get('auto_approved', 0)
            st.metric("Auto-Approved", auto_approved)
        else:
            st.metric("Auto-Approved", "N/A")
    
    with col3:
        if policy_data:
            escalated = policy_data.get('policy_stats', {}).get('escalated', 0)
            st.metric("Escalated", escalated)
        else:
            st.metric("Escalated", "N/A")
    
    with col4:
        # Calculate total predicted savings
        total_savings = sum(d.get('predicted_savings', 0) for d in decisions[-10:])
        st.metric("Recent Savings", f"${total_savings:.2f}")
    
    # Policy visibility section
    if policy_data:
        st.subheader("📋 Policy Visibility")
        
        policy_stats = policy_data.get('policy_stats', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success(f"✅ Auto-Approved: {policy_stats.get('auto_approved', 0)}")
        
        with col2:
            st.warning(f"⚠️ Escalated: {policy_stats.get('escalated', 0)}")
        
        with col3:
            st.info(f"⏳ Pending: {policy_stats.get('pending', 0)}")
    
    # Display recent decisions with enhanced information
    st.subheader("Recent Decisions")
    
    for decision in reversed(decisions[-10:]):  # Show last 10
        policy_status = decision.get('policy_status', 'pending')
        predicted_savings = decision.get('predicted_savings', 0)
        confidence = decision.get('confidence', 0)
        
        # Status indicator
        if policy_status == 'auto_approved':
            status_icon = "✅"
            status_color = "success"
        elif policy_status == 'escalated':
            status_icon = "⚠️"
            status_color = "warning"
        else:
            status_icon = "⏳"
            status_color = "info"
        
        with st.expander(
            f"{status_icon} {decision.get('service', 'Unknown')} - "
            f"{decision.get('current_provider', '?')} → {decision.get('recommended_provider', '?')} "
            f"({format_timestamp(decision.get('timestamp', ''))})"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Decision Details**")
                st.write(f"**Service:** {decision.get('service', 'N/A')}")
                st.write(f"**From:** {decision.get('current_provider', 'N/A')}")
                st.write(f"**To:** {decision.get('recommended_provider', 'N/A')}")
                st.write(f"**Confidence:** {confidence:.1%}")
                st.write(f"**Policy Status:** {policy_status.replace('_', ' ').title()}")
            
            with col2:
                st.markdown("**Impact Analysis**")
                st.write(f"**Predicted Savings:** ${predicted_savings:.2f}")
                st.write(f"**Reasoning:** {decision.get('reasoning', 'No reasoning provided')}")
                
                # Show confidence bar
                st.progress(confidence)
                st.caption(f"Confidence: {confidence:.1%}")
            
            # Show detailed explanation if available
            if 'explanation' in decision:
                st.markdown("**Detailed Explanation:**")
                st.write(decision['explanation'])
                st.write(f"**From:** {decision.get('current_provider', 'N/A')}")
                st.write(f"**To:** {decision.get('recommended_provider', 'N/A')}")
                st.write(f"**Confidence:** {decision.get('confidence', 0):.1%}")
            
            with col2:
                st.markdown("**Metrics**")
                scores = decision.get('scores', {})
                if scores:
                    for provider, score_data in scores.items():
                        if isinstance(score_data, dict):
                            st.write(f"**{provider.upper()}:** {score_data.get('total', 0):.3f}")
            
            st.markdown("**Explanation**")
            st.info(decision.get('explanation', 'No explanation available'))
            
            if 'git_branch' in decision:
                st.code(f"Git Branch: {decision['git_branch']}", language="bash")

def render_cost_analysis():
    """Render cost analysis tab."""
    st.header("💰 Cost Analysis")
    
    cost_data = fetch_data("/api/cost-analysis")
    telemetry = fetch_data("/api/telemetry")
    
    if not cost_data or not telemetry:
        st.warning("Unable to fetch cost data")
        return
    
    analysis = cost_data.get('analysis', {})
    
    # Provider comparison
    st.subheader("Provider Cost Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### AWS")
        st.metric("Services", analysis.get('aws', {}).get('services', 0))
        st.metric("Total Cost", f"${analysis.get('aws', {}).get('total_cost', 0):.2f}/hr")
        st.metric("Avg Latency", f"{analysis.get('aws', {}).get('avg_latency', 0):.1f}ms")
    
    with col2:
        st.markdown("### Alibaba Cloud")
        st.metric("Services", analysis.get('alibaba', {}).get('services', 0))
        st.metric("Total Cost", f"${analysis.get('alibaba', {}).get('total_cost', 0):.2f}/hr")
        st.metric("Avg Latency", f"{analysis.get('alibaba', {}).get('avg_latency', 0):.1f}ms")
    
    # Cost vs Latency scatter plot
    st.markdown("---")
    st.subheader("Cost vs Latency Analysis")
    
    telemetry_data = telemetry.get('data', {})
    
    plot_data = []
    for service, data in telemetry_data.items():
        if not isinstance(data, dict):
            continue
        
        for provider in ['aws', 'alibaba']:
            if provider in data:
                provider_data = data[provider]
                plot_data.append({
                    'Service': service,
                    'Provider': provider,
                    'Cost': provider_data.get('cost', 0),
                    'Latency': provider_data.get('latency', 0),
                    'GPUs': provider_data.get('available_gpus', 0)
                })
    
    if plot_data:
        df = pd.DataFrame(plot_data)
        
        fig = px.scatter(
            df,
            x='Latency',
            y='Cost',
            color='Provider',
            size='GPUs',
            hover_data=['Service'],
            color_discrete_map={'aws': '#FF9900', 'alibaba': '#FF6A00'},
            labels={'Latency': 'Latency (ms)', 'Cost': 'Cost ($/hr)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for visualization")

def render_telemetry():
    """Render telemetry tab."""
    st.header("📈 Live Telemetry")
    
    telemetry = fetch_data("/api/telemetry")
    
    if not telemetry:
        st.warning("Unable to fetch telemetry data")
        return
    
    telemetry_data = telemetry.get('data', {})
    
    if not telemetry_data:
        st.info("No telemetry data available")
        return
    
    # Display telemetry for each service
    for service, data in telemetry_data.items():
        if not isinstance(data, dict):
            continue
        
        st.subheader(f"🔧 {service}")
        
        current_provider = data.get('current_provider', 'unknown')
        st.markdown(f"**Current Provider:** `{current_provider.upper()}`")
        
        # Provider metrics comparison
        col1, col2 = st.columns(2)
        
        for idx, provider in enumerate(['aws', 'alibaba']):
            col = col1 if idx == 0 else col2
            
            with col:
                if provider in data:
                    provider_data = data[provider]
                    
                    is_current = provider == current_provider
                    header = f"{'✅ ' if is_current else ''}{provider.upper()}"
                    st.markdown(f"**{header}**")
                    
                    st.metric("Cost", f"${provider_data.get('cost', 0):.2f}/hr")
                    st.metric("Latency", f"{provider_data.get('latency', 0):.1f}ms")
                    st.metric("Credits", f"{provider_data.get('credits', 0):.2f}")
                    st.metric("GPUs", provider_data.get('available_gpus', 0))
                    st.caption(f"Region: {provider_data.get('region', 'N/A')}")
                    st.caption(f"Instance: {provider_data.get('instance', 'N/A')}")
        
        st.markdown("---")

def render_live_feed():
    """Render live feed tab."""
    st.header("⚡ Live Activity Feed")
    
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
                st.text(f"[{timestamp}] {service}: {decision.get('explanation', 'No details')}")

def render_health_check():
    """Render health check tab."""
    st.header("🏥 System Health Check")
    
    # Fetch health data
    health = fetch_data("/healthz")
    
    if not health:
        st.error("Unable to fetch health data")
        return
    
    # System status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = health.get('status', 'unknown')
        if status == 'ok':
            st.success("🟢 System Status: HEALTHY")
        else:
            st.error(f"🔴 System Status: {status.upper()}")
    
    with col2:
        st.metric("Active Providers", len(health.get('active_providers', [])))
    
    with col3:
        st.metric("Total Services", len(health.get('services', {})))
    
    with col4:
        last_commit = health.get('last_ai_commit', 'N/A')
        st.metric("Last AI Commit", last_commit[:8] if last_commit != 'N/A' else 'N/A')
    
    # Detailed health information
    st.subheader("Detailed System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Active Providers:**")
        for provider in health.get('active_providers', []):
            st.markdown(f"- {provider.upper()}")
    
    with col2:
        st.markdown("**Service Distribution:**")
        services = health.get('services', {})
        for service, provider in services.items():
            st.markdown(f"- {service}: {provider.upper()}")
    
    # API endpoint status
    st.subheader("API Endpoint Status")
    
    endpoints = [
        ("/healthz", "Health Check"),
        ("/api/telemetry", "Telemetry Data"),
        ("/api/decisions", "AI Decisions"),
        ("/api/metrics", "System Metrics"),
        ("/api/cost-analysis", "Cost Analysis"),
        ("/api/policy-visibility", "Policy Visibility"),
        ("/api/gitops-history", "GitOps History"),
        ("/api/economics-view", "Economics View")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_URL}{endpoint}", timeout=3)
            if response.status_code == 200:
                st.success(f"✅ {description} ({endpoint})")
            else:
                st.warning(f"⚠️ {description} ({endpoint}) - Status: {response.status_code}")
        except:
            st.error(f"❌ {description} ({endpoint}) - Unreachable")

def render_gitops_history():
    """Render GitOps history tab."""
    st.header("📋 GitOps History")
    
    # Fetch GitOps history
    gitops_data = fetch_data("/api/gitops-history")
    
    if not gitops_data:
        st.warning("Unable to fetch GitOps history")
        return
    
    gitops_history = gitops_data.get('gitops_history', [])
    total_commits = gitops_data.get('total_commits', 0)
    
    st.metric("Total Commits", total_commits)
    
    if not gitops_history:
        st.info("No GitOps history available")
        return
    
    # Display recent GitOps activities
    st.subheader("Recent GitOps Activities")
    
    for activity in reversed(gitops_history[-20:]):  # Show last 20
        with st.expander(
            f"🔧 {activity.get('service', 'Unknown')} - "
            f"{activity.get('action', 'unknown')} "
            f"({format_timestamp(activity.get('timestamp', ''))})"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Service:** {activity.get('service', 'N/A')}")
                st.markdown(f"**Action:** {activity.get('action', 'N/A')}")
                st.markdown(f"**Git Branch:** `{activity.get('git_branch', 'N/A')}`")
                st.markdown(f"**Commit Hash:** `{activity.get('commit_hash', 'N/A')}`")
            
            with col2:
                st.markdown(f"**Predicted Savings:** ${activity.get('predicted_savings', 0):.2f}")
                st.markdown(f"**Confidence:** {activity.get('confidence', 0):.1%}")
                st.markdown(f"**Policy Status:** {activity.get('policy_status', 'pending')}")
            
            st.markdown("**Reasoning:**")
            st.markdown(f"_{activity.get('reasoning', 'No reasoning provided')}_")

def render_economics_view():
    """Render economics view tab."""
    st.header("💸 Economics View")
    
    # Fetch economics data
    economics_data = fetch_data("/api/economics-view")
    
    if not economics_data:
        st.warning("Unable to fetch economics data")
        return
    
    total_spend = economics_data.get('total_spend', {})
    provider_breakdown = economics_data.get('provider_breakdown', {})
    predicted_savings = economics_data.get('predicted_savings', {})
    
    # Total spend overview
    st.subheader("💰 Total Platform Spend")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Hourly Spend",
            f"${total_spend.get('hourly', 0):.2f}",
            help="Current hourly spend across all providers"
        )
    
    with col2:
        st.metric(
            "Daily Spend",
            f"${total_spend.get('daily', 0):.2f}",
            help="Projected daily spend"
        )
    
    with col3:
        st.metric(
            "Monthly Spend",
            f"${total_spend.get('monthly', 0):.2f}",
            help="Projected monthly spend"
        )
    
    # Provider breakdown
    st.subheader("📊 Provider Spend Breakdown")
    
    col1, col2 = st.columns(2)
    
    for idx, (provider, data) in enumerate(provider_breakdown.items()):
        col = col1 if idx == 0 else col2
        
        with col:
            st.markdown(f"**{provider.upper()}**")
            st.metric("Hourly Spend", f"${data.get('hourly', 0):.2f}")
            st.metric("Monthly Spend", f"${data.get('monthly', 0):.2f}")
            st.metric("Services", data.get('services', 0))
            st.metric("Percentage", f"{data.get('percentage', 0):.1f}%")
    
    # Predicted savings
    st.subheader("🎯 AI Predicted Savings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Predicted Savings",
            f"${predicted_savings.get('total', 0):.2f}",
            help="Total savings from recent AI decisions"
        )
    
    with col2:
        st.metric(
            "Monthly Projection",
            f"${predicted_savings.get('monthly_projection', 0):.2f}",
            help="Projected monthly savings"
        )
    
    # Spend trend visualization
    st.subheader("📈 Spend Trend Analysis")
    
    # Create a simple spend trend chart
    providers = list(provider_breakdown.keys())
    hourly_spends = [provider_breakdown[p].get('hourly', 0) for p in providers]
    monthly_spends = [provider_breakdown[p].get('monthly', 0) for p in providers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Hourly Spend',
        x=providers,
        y=hourly_spends,
        marker_color=['#FF9900', '#FF6A00']
    ))
    
    fig.add_trace(go.Bar(
        name='Monthly Spend',
        x=providers,
        y=[m/24/30 for m in monthly_spends],  # Convert to hourly equivalent for comparison
        marker_color=['#FFB84D', '#FF8A33'],
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Provider Spend Comparison",
        xaxis_title="Provider",
        yaxis_title="Spend ($/hour)",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Alert section
    st.subheader("🚨 Cost Alerts & Anomalies")
    
    # Check for potential cost anomalies
    total_hourly = total_spend.get('hourly', 0)
    if total_hourly > 100:
        st.warning("⚠️ High hourly spend detected (>$100/hr)")
    elif total_hourly > 50:
        st.info("ℹ️ Moderate hourly spend detected (>$50/hr)")
    else:
        st.success("✅ Normal spend levels")
    
    # Price spike simulation
    st.markdown("---")
    st.subheader("🧪 Price Spike Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        spike_provider = st.selectbox("Select Provider for Spike", ["aws", "alibaba"])
    
    with col2:
        spike_percentage = st.slider("Spike Percentage", 10, 200, 50)
    
    if st.button("🚀 Simulate Price Spike", type="primary"):
        spike_data = {
            "provider": spike_provider,
            "spike_percentage": spike_percentage
        }
        
        try:
            response = requests.post(f"{API_URL}/api/simulate-price-spike", json=spike_data)
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Price spike simulated for {spike_provider}")
                st.info(f"**AI Response:** {result.get('ai_response', 'No response')}")
                st.warning(f"**Estimated Impact:** {result.get('estimated_impact', 'Unknown')}")
                
                # Show potential impact
                current_spend = provider_breakdown.get(spike_provider, {}).get('hourly', 0)
                new_spend = current_spend * (1 + spike_percentage / 100)
                impact = new_spend - current_spend
                
                st.metric(
                    f"Potential {spike_provider.upper()} Impact",
                    f"+${impact:.2f}/hr",
                    delta=f"+{spike_percentage}%"
                )
            else:
                st.error("Failed to simulate price spike")
        except Exception as e:
            st.error(f"Error simulating price spike: {e}")

def render_finops_policy():
    """Render FinOps & Policy Intelligence dashboard."""
    st.header("⚖️ FinOps & Policy Intelligence")
    
    # Fetch budget and policy data
    budget_data = fetch_data("/api/budget-status")
    policy_data = fetch_data("/api/policy-stats")
    
    if not budget_data or not policy_data:
        st.warning("Unable to fetch FinOps and policy data")
        return
    
    budget_status = budget_data.get('budget_status', {})
    policy_stats = policy_data.get('policy_stats', {})
    recent_decisions = policy_data.get('recent_decisions', [])
    
    # Budget Overview
    st.subheader("💰 Budget Management")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Monthly Budget",
            f"${budget_status.get('monthly_budget', 0):,.0f}",
            help="Total monthly budget allocation"
        )
    
    with col2:
        utilization = budget_status.get('utilization_percent', 0)
        st.metric(
            "Budget Utilization",
            f"{utilization:.1f}%",
            delta=f"{utilization - 25:.1f}%" if utilization > 25 else None,
            help="Current budget utilization percentage"
        )
    
    with col3:
        st.metric(
            "Credits Available",
            f"${budget_status.get('credits_available', 0):,.0f}",
            help="Available cloud credits"
        )
    
    with col4:
        remaining = budget_status.get('budget_remaining', 0)
        st.metric(
            "Budget Remaining",
            f"${remaining:,.0f}",
            delta=f"-${budget_status.get('current_spend', 0):,.0f}" if remaining < budget_status.get('monthly_budget', 0) else None,
            help="Remaining budget for the month"
        )
    
    # Budget alerts
    if budget_status.get('is_over_budget', False):
        st.error("🚨 **OVER BUDGET ALERT** - Current spend exceeds monthly budget!")
    elif budget_status.get('needs_alert', False):
        st.warning("⚠️ **BUDGET ALERT** - Approaching budget threshold")
    else:
        st.success("✅ Budget within normal limits")
    
    # Policy Statistics
    st.subheader("📋 Policy Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Decisions",
            policy_stats.get('total_decisions', 0),
            help="Total AI decisions evaluated"
        )
    
    with col2:
        auto_approved = policy_stats.get('auto_approved', 0)
        st.metric(
            "Auto-Approved",
            auto_approved,
            delta=f"+{auto_approved}" if auto_approved > 0 else None,
            help="Decisions automatically approved by policy"
        )
    
    with col3:
        escalated = policy_stats.get('escalated', 0)
        st.metric(
            "Escalated",
            escalated,
            delta=f"+{escalated}" if escalated > 0 else None,
            help="Decisions requiring manual review"
        )
    
    with col4:
        pending = policy_stats.get('pending', 0)
        st.metric(
            "Pending",
            pending,
            delta=f"+{pending}" if pending > 0 else None,
            help="Decisions pending policy evaluation"
        )
    
    # Policy Visualization
    st.subheader("📊 Policy Decision Distribution")
    
    if policy_stats.get('total_decisions', 0) > 0:
        decision_data = {
            'Auto-Approved': policy_stats.get('auto_approved', 0),
            'Escalated': policy_stats.get('escalated', 0),
            'Pending': policy_stats.get('pending', 0),
            'Rejected': policy_stats.get('rejected', 0)
        }
        
        # Remove zero values
        decision_data = {k: v for k, v in decision_data.items() if v > 0}
        
        if decision_data:
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
        else:
            st.info("No policy decisions recorded yet")
    else:
        st.info("No policy decisions recorded yet")
    
    # Regional Discounts
    st.subheader("🌍 Regional Discounts")
    
    regional_discounts = budget_status.get('regional_discounts', {})
    if regional_discounts:
        discount_df = pd.DataFrame([
            {"Region": region, "Discount": f"{discount*100:.1f}%"}
            for region, discount in regional_discounts.items()
        ])
        
        st.dataframe(
            discount_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No regional discounts configured")
    
    # Recent Policy Decisions
    st.subheader("📝 Recent Policy Decisions")
    
    if recent_decisions:
        for decision in reversed(recent_decisions[-10:]):  # Show last 10
            policy_status = decision.get('policy_status', 'pending')
            
            # Status indicator
            if policy_status == 'auto_approved':
                status_icon = "✅"
                status_color = "success"
            elif policy_status == 'escalated':
                status_icon = "⚠️"
                status_color = "warning"
            elif policy_status == 'rejected':
                status_icon = "❌"
                status_color = "error"
            else:
                status_icon = "⏳"
                status_color = "info"
            
            with st.expander(
                f"{status_icon} {decision.get('service', 'Unknown')} - "
                f"{policy_status.replace('_', ' ').title()} "
                f"({format_timestamp(decision.get('timestamp', ''))})"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Service:** {decision.get('service', 'N/A')}")
                    st.markdown(f"**Policy Status:** {policy_status.replace('_', ' ').title()}")
                    st.markdown(f"**Cost Delta:** {decision.get('cost_delta_percent', 0):.1f}%")
                    st.markdown(f"**Predicted Savings:** ${decision.get('predicted_savings', 0):.2f}")
                
                with col2:
                    st.markdown(f"**Confidence:** {decision.get('confidence', 0):.1%}")
                    st.markdown(f"**Budget Impact:** ${decision.get('budget_impact', 0):.2f}")
                    st.markdown(f"**Credit Utilization:** ${decision.get('credit_utilization', 0):.2f}")
                
                # Policy violations
                violations = decision.get('policy_violations', [])
                if violations:
                    st.markdown("**Policy Violations:**")
                    for violation in violations:
                        st.markdown(f"- {violation}")
                
                # Reasoning
                reasoning = decision.get('reasoning', 'No reasoning provided')
                st.markdown("**Policy Reasoning:**")
                st.markdown(f"_{reasoning}_")
    else:
        st.info("No recent policy decisions available")
    
    # Policy Configuration
    st.subheader("⚙️ Policy Configuration")
    
    with st.expander("View Policy Rules"):
        st.markdown("""
        **Auto-Approval Criteria:**
        - Cost delta ≤ 5% of current cost
        - AI confidence ≥ 85%
        - Predicted monthly savings ≥ $50
        - Service tier is not critical (Tier 1)
        - Budget impact ≤ 10% of monthly budget
        - Sufficient credits available
        
        **Manual Approval Required:**
        - High-impact changes (>5% cost delta)
        - Critical services (Tier 1)
        - Low confidence decisions (<85%)
        - Budget impact >10% of monthly budget
        - Insufficient credits
        """)
    
    # Budget Management Actions
    st.subheader("🔧 Budget Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Budget Status", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Generate Budget Report"):
            st.info("Budget report generation would be implemented here")

def render_grafana():
    """Render Grafana dashboard integration."""
    st.header("📊 Grafana Dashboard")
    
    # Grafana connection status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            response = requests.get("http://localhost:3001/api/health", timeout=3)
            if response.status_code == 200:
                st.success("🟢 Grafana Connected")
            else:
                st.warning("🟡 Grafana Limited Access")
        except:
            st.error("🔴 Grafana Offline")
    
    with col2:
        try:
            response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=3)
            if response.status_code == 200:
                st.success("🟢 Prometheus Connected")
            else:
                st.warning("🟡 Prometheus Limited Access")
        except:
            st.error("🔴 Prometheus Offline")
    
    with col3:
        try:
            response = requests.get("http://localhost:8001/healthz", timeout=3)
            if response.status_code == 200:
                st.success("🟢 API Connected")
            else:
                st.warning("🟡 API Limited Access")
        except:
            st.error("🔴 API Offline")
    
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
            st.markdown("""
            <script>
            window.open('http://localhost:3001', '_blank');
            </script>
            """, unsafe_allow_html=True)
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
    
    # Mock Grafana panel data
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
                    # Provider comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("AWS", f"{data['aws']:.1f}")
                    with col2:
                        st.metric("Alibaba", f"{data['alibaba']:.1f}")
                else:
                    # Other metrics
                    for key, value in data.items():
                        st.metric(key.replace('_', ' ').title(), value)
    
    # Grafana configuration
    st.subheader("⚙️ Grafana Configuration")
    
    with st.expander("View Configuration Details"):
        st.markdown("""
        **Data Source:** Prometheus (http://prometheus:9090)  
        **Dashboard ID:** 1  
        **Refresh Interval:** 10s  
        **Time Range:** Last 1 hour  
        **Variables:** provider, service, region  
        
        **Key Metrics:**
        - `swen_cpu_utilization{service="service1",provider="aws"}`
        - `swen_memory_utilization{service="service1",provider="aws"}`
        - `swen_network_io{service="service1",provider="aws"}`
        - `swen_ai_decisions_total`
        - `swen_service_distribution{provider="aws"}`
        """)
    
    # Grafana alerts
    st.subheader("🚨 Grafana Alerts")
    
    alert_data = [
        {"name": "High CPU Usage", "status": "OK", "threshold": ">80%"},
        {"name": "Memory Pressure", "status": "WARNING", "threshold": ">90%"},
        {"name": "Network Latency", "status": "OK", "threshold": ">100ms"},
        {"name": "AI Decision Failure", "status": "OK", "threshold": ">5 failures/hour"}
    ]
    
    for alert in alert_data:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{alert['name']}**")
        with col2:
            if alert['status'] == 'OK':
                st.success(alert['status'])
            elif alert['status'] == 'WARNING':
                st.warning(alert['status'])
            else:
                st.error(alert['status'])
        with col3:
            st.caption(alert['threshold'])

def render_prometheus():
    """Render Prometheus metrics and queries."""
    st.header("🔍 Prometheus Metrics")
    
    # Prometheus connection status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=3)
            if response.status_code == 200:
                st.success("🟢 Prometheus Connected")
            else:
                st.warning("🟡 Prometheus Limited Access")
        except:
            st.error("🔴 Prometheus Offline")
    
    with col2:
        try:
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=3)
            if response.status_code == 200:
                targets_data = response.json()
                active_targets = len([t for t in targets_data.get('data', {}).get('activeTargets', []) if t.get('health') == 'up'])
                st.success(f"🟢 {active_targets} Active Targets")
            else:
                st.warning("🟡 Targets Limited Access")
        except:
            st.error("🔴 Targets Offline")
    
    with col3:
        try:
            response = requests.get("http://localhost:8001/metrics", timeout=3)
            if response.status_code == 200:
                st.success("🟢 Metrics Endpoint Active")
            else:
                st.warning("🟡 Metrics Limited Access")
        except:
            st.error("🔴 Metrics Offline")
    
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
    
    # Query examples
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
                try:
                    response = requests.get(f"http://localhost:9090/api/v1/query?query={query['query']}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        st.success("✅ Query executed successfully!")
                        st.json(data)
                    else:
                        st.error(f"❌ Query failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Query error: {e}")
    
    # Prometheus configuration
    st.subheader("⚙️ Prometheus Configuration")
    
    with st.expander("View Configuration"):
        st.markdown("""
        **Configuration File:** `ops/prometheus-simple.yml`  
        **Scrape Interval:** 15s  
        **Evaluation Interval:** 15s  
        **Retention:** 15d  
        
        **Active Jobs:**
        - `swen-dashboard-api` → `host.docker.internal:8001/metrics`
        - `prometheus` → `localhost:9090/metrics`
        
        **Inactive Jobs:**
        - `node-exporter-aws` → `node-exporter-aws:9100/metrics`
        - `node-exporter-alibaba` → `node-exporter-alibaba:9100/metrics`
        - `swen-ai-engine` → `ai-engine:9100/metrics`
        """)
    
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
            st.markdown("""
            <script>
            window.open('http://localhost:9090', '_blank');
            </script>
            """, unsafe_allow_html=True)
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
