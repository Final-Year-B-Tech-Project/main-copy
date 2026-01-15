#!/usr/bin/env python3
"""
Test script to verify proctoring system is working
"""

import requests
import json
import time

def test_proctoring_system():
    base_url = 'http://127.0.0.1:5000'
    
    print("🔍 Testing Proctoring System Integration...")
    print("=" * 50)
    
    # Test 1: Check if proctoring test endpoint works
    try:
        print("1. Testing proctoring system availability...")
        response = requests.get(f'{base_url}/api/proctoring/test', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   ✅ System Type: {data.get('system_type', 'Unknown')}")
            print(f"   ✅ Models Loaded: {data.get('models_loaded', {})}")
            print(f"   ✅ Test Results: {data.get('test_results', {}).get('success', False)}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Make sure Flask server is running: python3 run_project.py")
    print("2. Go to: http://127.0.0.1:5000")
    print("3. Register as student")
    print("4. Start practice interview")
    print("5. Allow camera access")
    print("6. Hold up phone to test detection")
    print("7. Look away to test gaze detection")
    print("8. Watch proctoring status indicator")

if __name__ == '__main__':
    test_proctoring_system()