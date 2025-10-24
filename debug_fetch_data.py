#!/usr/bin/env python3
"""Minimal test to debug the fetch_data issue."""

import requests
import json

def test_direct_api_call():
    """Test direct API call."""
    try:
        response = requests.get("http://localhost:8001/api/deployments", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            data = response.json()
            print(f"Parsed data: {json.dumps(data, indent=2)}")
            return data
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_fetch_data_simulation():
    """Simulate the dashboard's fetch_data function."""
    try:
        response = requests.get("http://localhost:8001/api/deployments", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"fetch_data error: {e}")
        return None

if __name__ == "__main__":
    print("=== Direct API Call Test ===")
    data1 = test_direct_api_call()
    
    print("\n=== fetch_data Simulation Test ===")
    data2 = test_fetch_data_simulation()
    
    print(f"\nData1: {data1}")
    print(f"Data2: {data2}")
    print(f"Equal: {data1 == data2}")
