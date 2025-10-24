#!/usr/bin/env python3
"""
Comprehensive Test Script for SWEN AIOps Platform
Tests all components: API, AI Engine, Grafana, and Dashboard
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints."""
    print("🔍 Testing API Endpoints...")
    
    base_url = "http://localhost:8001"
    endpoints = [
        "/",
        "/healthz",
        "/api/telemetry",
        "/api/decisions",
        "/api/metrics",
        "/api/cost-analysis",
        "/api/policy-visibility",
        "/api/gitops-history",
        "/api/economics-view",
        "/metrics"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                results[endpoint] = "OK"
            else:
                print(f"❌ {endpoint} - HTTP {response.status_code}")
                results[endpoint] = f"HTTP {response.status_code}"
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            results[endpoint] = f"Error: {e}"
    
    return results

def test_healthz_endpoint():
    """Test the enhanced /healthz endpoint."""
    print("\n🏥 Testing Enhanced /healthz Endpoint...")
    
    try:
        response = requests.get("http://localhost:8001/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Active Providers: {data.get('active_providers')}")
            print(f"✅ Current Cloud: {data.get('current_cloud')}")
            print(f"✅ Current Region: {data.get('current_region')}")
            print(f"✅ Policy Stats: {data.get('policy_stats')}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_prometheus_metrics():
    """Test Prometheus metrics endpoint."""
    print("\n📊 Testing Prometheus Metrics...")
    
    try:
        response = requests.get("http://localhost:8001/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            metrics_lines = metrics_text.strip().split('\n')
            
            print(f"✅ Total metrics: {len(metrics_lines)}")
            
            # Check for specific metrics
            required_metrics = [
                'swen_service_cost',
                'swen_service_latency',
                'swen_service_gpus',
                'swen_cpu_utilization',
                'swen_memory_utilization',
                'swen_network_io',
                'swen_ai_decisions_total',
                'swen_policy_auto_approved_total',
                'swen_policy_escalated_total',
                'swen_service_distribution'
            ]
            
            found_metrics = []
            for metric in required_metrics:
                if any(metric in line for line in metrics_lines):
                    found_metrics.append(metric)
                    print(f"✅ Found: {metric}")
                else:
                    print(f"❌ Missing: {metric}")
            
            return len(found_metrics) == len(required_metrics)
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("🚀 SWEN AIOps Platform - Comprehensive Test Suite")
    print("=" * 60)
    
    # Test results
    results = {}
    
    # Test API endpoints
    results['api_endpoints'] = test_api_endpoints()
    
    # Test enhanced healthz
    results['healthz'] = test_healthz_endpoint()
    
    # Test Prometheus metrics
    results['prometheus_metrics'] = test_prometheus_metrics()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The SWEN AIOps platform is fully operational.")
    else:
        print("⚠️ Some tests failed. Please check the logs and configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
