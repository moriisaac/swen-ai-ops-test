#!/usr/bin/env python3
"""
SWEN AIOps Grafana Setup Test
Tests the complete observability stack: API → Prometheus → Grafana
"""

import requests
import time
import json
from datetime import datetime

def test_api_metrics():
    """Test if API is exposing Prometheus metrics."""
    try:
        response = requests.get("http://localhost:8001/metrics", timeout=5)
        if response.status_code == 200:
            print("✅ API metrics endpoint is working")
            print("📊 Sample metrics:")
            lines = response.text.split('\n')[:10]  # First 10 lines
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print(f"❌ API metrics endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API metrics endpoint failed: {e}")
        return False

def test_prometheus():
    """Test if Prometheus is scraping the API."""
    try:
        # Check if Prometheus is running
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        if response.status_code == 200:
            targets = response.json()
            print("✅ Prometheus is running")
            
            # Check if our API target is up
            for target in targets.get('data', {}).get('activeTargets', []):
                if 'swen-dashboard-api' in target.get('job', ''):
                    if target.get('health') == 'up':
                        print("✅ Prometheus is successfully scraping API")
                        print(f"   Target: {target.get('scrapeUrl', '')}")
                        return True
                    else:
                        print(f"❌ Prometheus target is down: {target.get('lastError', 'Unknown error')}")
                        return False
            
            print("❌ Prometheus target for API not found")
            return False
        else:
            print(f"❌ Prometheus API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prometheus test failed: {e}")
        return False

def test_grafana():
    """Test if Grafana is accessible."""
    try:
        response = requests.get("http://localhost:3001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Grafana is running")
            print("🌐 Access Grafana at: http://localhost:3001")
            print("   Username: admin")
            print("   Password: admin")
            return True
        else:
            print(f"❌ Grafana health check returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Grafana test failed: {e}")
        return False

def test_telemetry_data():
    """Test if telemetry data is being generated."""
    try:
        response = requests.get("http://localhost:8001/api/telemetry", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Telemetry data is available")
            
            # Check for latency data
            for service, service_data in data.items():
                if isinstance(service_data, dict):
                    for provider in ['aws', 'alibaba']:
                        if provider in service_data:
                            provider_data = service_data[provider]
                            latency = provider_data.get('latency', 0)
                            cost = provider_data.get('cost', 0)
                            print(f"   {service} ({provider}): latency={latency}ms, cost=${cost}/hr")
            
            return True
        else:
            print(f"❌ Telemetry endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telemetry test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 SWEN AIOps Observability Stack Test")
    print("=" * 50)
    
    # Test telemetry data
    print("\n📊 Testing Telemetry Data...")
    telemetry_ok = test_telemetry_data()
    
    # Test API metrics
    print("\n🔌 Testing API Metrics...")
    api_ok = test_api_metrics()
    
    # Test Prometheus
    print("\n📈 Testing Prometheus...")
    prometheus_ok = test_prometheus()
    
    # Test Grafana
    print("\n📊 Testing Grafana...")
    grafana_ok = test_grafana()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Telemetry Data: {'✅' if telemetry_ok else '❌'}")
    print(f"   API Metrics:    {'✅' if api_ok else '❌'}")
    print(f"   Prometheus:     {'✅' if prometheus_ok else '❌'}")
    print(f"   Grafana:        {'✅' if grafana_ok else '❌'}")
    
    if all([telemetry_ok, api_ok, prometheus_ok, grafana_ok]):
        print("\n🎉 All tests passed! Observability stack is working correctly.")
        print("\n🌐 Access URLs:")
        print("   • Grafana Dashboard: http://localhost:3001")
        print("   • Prometheus:        http://localhost:9090")
        print("   • API Metrics:       http://localhost:8001/metrics")
        print("   • Telemetry Data:    http://localhost:8001/api/telemetry")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure API server is running: python dashboard/api/main.py")
        print("   2. Start observability stack: docker-compose up -d")
        print("   3. Check Prometheus targets: http://localhost:9090/targets")
        print("   4. Check Grafana datasources: http://localhost:3001/datasources")

if __name__ == "__main__":
    main()
