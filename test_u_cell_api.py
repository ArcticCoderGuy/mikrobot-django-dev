#!/usr/bin/env python
"""
Test script for U-Cell API endpoints
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

def test_u_cell_endpoints():
    """Test all U-Cell API endpoints"""
    
    base_url = "http://localhost:8000/api/v1/u-cell"
    
    endpoints = [
        "/validations/",
        "/risk-assessments/", 
        "/executions/",
        "/quality-measurements/",
        "/system-health/"
    ]
    
    print(f"Testing U-Cell API Endpoints at {base_url}")
    print("=" * 60)
    
    results = {}
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 301, 302],
                'content_type': response.headers.get('content-type', ''),
                'response_length': len(response.text)
            }
            
            if response.status_code == 200:
                print(f"SUCCESS: {response.status_code} - {len(response.text)} chars")
            else:
                print(f"FAILED: {response.status_code}")
                if response.status_code == 404:
                    print(f"   URL not found: {url}")
                    
        except requests.exceptions.ConnectionError:
            results[endpoint] = {
                'status_code': 'CONNECTION_ERROR',
                'success': False,
                'error': 'Could not connect to Django server'
            }
            print(f"CONNECTION ERROR: Django server not running?")
            
        except Exception as e:
            results[endpoint] = {
                'status_code': 'ERROR',
                'success': False,
                'error': str(e)
            }
            print(f"ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("U-CELL API TEST SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    
    for endpoint, result in results.items():
        status = "PASS" if result.get('success') else "FAIL"
        print(f"{status} {endpoint} - {result.get('status_code', 'N/A')}")
    
    print(f"\nResults: {successful}/{total} endpoints working")
    
    if successful == total:
        print("ALL U-CELL ENDPOINTS ARE WORKING!")
        return True
    else:
        print("Some endpoints need attention")
        return False

if __name__ == "__main__":
    success = test_u_cell_endpoints()
    sys.exit(0 if success else 1)