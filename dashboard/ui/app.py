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
API_URL = st.sidebar.text_input("API URL", "http://localhost:8001")
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
        st.error(f"Error fetching data from {endpoint}: {e}")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🤖 AI Decisions", 
        "💰 Cost Analysis", 
        "📈 Telemetry", 
        "⚡ Live Feed"
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
    
    if not decisions_data:
        st.warning("Unable to fetch AI decisions")
        return
    
    decisions = decisions_data.get('decisions', [])
    
    if not decisions:
        st.info("No AI decisions recorded yet")
        return
    
    st.metric("Total Decisions", decisions_data.get('total', 0))
    
    # Display recent decisions
    st.subheader("Recent Decisions")
    
    for decision in reversed(decisions[-10:]):  # Show last 10
        with st.expander(
            f"🔄 {decision.get('service', 'Unknown')} - "
            f"{decision.get('current_provider', '?')} → {decision.get('recommended_provider', '?')} "
            f"({format_timestamp(decision.get('timestamp', ''))})"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Decision Details**")
                st.write(f"**Service:** {decision.get('service', 'N/A')}")
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

if __name__ == "__main__":
    main()
