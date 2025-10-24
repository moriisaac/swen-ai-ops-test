#!/usr/bin/env python3
"""Test script to verify deployments tab functionality."""

import requests
import json

def test_deployments_tab():
    """Test the deployments tab functionality."""
    print("Testing Deployments Tab Functionality...")
    
    # Test API connection
    api_url = "http://localhost:8001"
    endpoint = "/api/deployments"
    
    try:
        response = requests.get(f"{api_url}{endpoint}", timeout=5)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response Data: {json.dumps(data, indent=2)}")
            
            # Test data parsing
            deployments = data.get('deployments', [])
            total_deployments = data.get('total_deployments', 0)
            
            print(f"\nParsed Data:")
            print(f"- Total Deployments: {total_deployments}")
            print(f"- Deployments Count: {len(deployments)}")
            
            # Test metrics calculation
            auto_approved = len([d for d in deployments if d.get('auto_approved', False)])
            manual_deployments = total_deployments - auto_approved
            success_rate = len([d for d in deployments if d.get('status') == 'success']) / max(total_deployments, 1) * 100
            
            print(f"\nCalculated Metrics:")
            print(f"- Auto-Approved: {auto_approved}")
            print(f"- Manual Deployments: {manual_deployments}")
            print(f"- Success Rate: {success_rate:.1f}%")
            
            # Test deployment details
            print(f"\nDeployment Details:")
            for i, deployment in enumerate(deployments[:3]):  # Show first 3
                print(f"  {i+1}. {deployment.get('branch', 'unknown')} - {deployment.get('status', 'unknown')}")
            
            return True
        else:
            print(f"API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

if __name__ == "__main__":
    success = test_deployments_tab()
    print(f"\nTest Result: {'✅ PASSED' if success else '❌ FAILED'}")
