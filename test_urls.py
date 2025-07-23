#!/usr/bin/env python
"""
Test Django URL configuration for U-Cell endpoints
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse, NoReverseMatch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_mcp.settings')
django.setup()

def test_u_cell_urls():
    """Test U-Cell URL patterns"""
    
    print("Testing U-Cell URL Configuration")
    print("=" * 50)
    
    client = Client()
    
    # Test endpoints
    endpoints = [
        '/api/v1/u-cell/validations/',
        '/api/v1/u-cell/risk-assessments/',
        '/api/v1/u-cell/executions/',
        '/api/v1/u-cell/quality-measurements/',
        '/api/v1/u-cell/system-health/'
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        
        try:
            response = client.get(endpoint)
            results[endpoint] = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 301, 302, 405],  # 405 = Method not allowed but URL exists
                'content_type': response.get('content-type', '') if hasattr(response, 'get') else ''
            }
            
            if response.status_code == 200:
                print(f"SUCCESS: {response.status_code}")
            elif response.status_code == 405:
                print(f"URL EXISTS: {response.status_code} (Method not allowed - normal for DRF)")
            else:
                print(f"FAILED: {response.status_code}")
                
        except Exception as e:
            results[endpoint] = {
                'status_code': 'ERROR',
                'success': False,
                'error': str(e)
            }
            print(f"ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("URL TEST SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    
    for endpoint, result in results.items():
        status = "PASS" if result.get('success') else "FAIL"
        print(f"{status} {endpoint} - {result.get('status_code', 'N/A')}")
    
    print(f"\nResults: {successful}/{total} endpoints accessible")
    
    if successful == total:
        print("ALL U-CELL ENDPOINTS ARE ACCESSIBLE!")
        return True
    else:
        print("Some endpoints need attention")
        return False

if __name__ == "__main__":
    success = test_u_cell_urls() 
    sys.exit(0 if success else 1)