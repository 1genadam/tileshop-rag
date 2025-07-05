#!/usr/bin/env python3
"""
Test External Links & Actions functionality
Debug why external links might not be working in dashboard
"""

import requests
import json

def test_external_links_functionality():
    """Test the external links functionality by checking a sample product"""
    print("🔗 Testing External Links & Actions Functionality")
    print("=" * 60)
    
    # Test the dashboard API endpoint for product data
    try:
        # Test with the sample SKU from our earlier test
        test_sku = "616601"
        dashboard_url = "http://127.0.0.1:8080"
        
        print(f"Testing SKU lookup for: {test_sku}")
        print(f"Dashboard URL: {dashboard_url}")
        
        # Test the API endpoint that provides product data to the dashboard
        api_url = f"{dashboard_url}/api/database/product/sku/{test_sku}"
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response size: {len(str(data))} characters")
            
            # Check if we have product data
            if data and data.get('success') and 'product' in data:
                product = data['product']
                print(f"✅ Product found: {product.get('title', 'No title')[:50]}...")
                
                # Check external links data structure
                print(f"\n🔍 External Links Data Analysis:")
                
                # Check primary URL
                primary_url = product.get('url')
                print(f"   Primary URL: {primary_url}")
                
                # Check for color variations
                color_variations = product.get('color_variations', [])
                print(f"   Color Variations: {len(color_variations)} found")
                
                # Check for batch URLs
                batch_urls = product.get('batch_urls', [])
                print(f"   Batch URLs: {len(batch_urls)} found")
                
                # Check for collection links
                collection_links = product.get('collection_links')
                print(f"   Collection Links: {collection_links}")
                
                # Summary for dashboard functionality
                has_external_links = bool(primary_url or color_variations or batch_urls)
                print(f"\n🎯 External Links Status: {'✅ AVAILABLE' if has_external_links else '❌ NO LINKS'}")
                
                if has_external_links:
                    print("   Dashboard should display External Links & Actions section")
                else:
                    print("   Dashboard may not show External Links & Actions section")
                    
            else:
                print(f"❌ No product found for SKU: {test_sku}")
                print("   This could explain why External Links & Actions is not showing")
                
        else:
            print(f"❌ API Request failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - Dashboard not running")
        print("   Start dashboard with: python3 reboot_dashboard.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    print(f"\n📋 Recommendations:")
    print("1. Ensure dashboard is running: python3 reboot_dashboard.py")
    print("2. Check that product data has proper URL fields")
    print("3. Verify product search is returning results")
    print("4. Test with a known good SKU that has external links")

if __name__ == "__main__":
    test_external_links_functionality()