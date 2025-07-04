#!/usr/bin/env python3
"""
Verify that SKU 485020 application extraction fix works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from curl_scraper import scrape_product_with_curl

def verify_fix():
    print("🔍 Verifying SKU 485020 Application Extraction Fix")
    print("=" * 60)
    
    url = "https://www.tileshop.com/products/linewood-white-matte-ceramic-wall-tile-12-x-36-in-485020"
    
    try:
        print(f"📥 Testing extraction for: {url}")
        
        # Use the proven curl-based approach
        result = scrape_product_with_curl(url)
        
        if result:
            print("✅ Extraction completed successfully")
            print()
            print("📊 VERIFICATION RESULTS:")
            print(f"   SKU: {result.get('sku', 'N/A')}")
            print(f"   🎯 Application Areas: {result.get('application_areas', 'N/A')}")
            print(f"   🎯 Typical Use Cases: {result.get('typical_use_cases', 'N/A')}")
            print(f"   Category: {result.get('category', 'N/A')}")
            print(f"   Subcategory: {result.get('subcategory', 'N/A')}")
            print(f"   Product Type: {result.get('product_type', 'N/A')}")
            print()
            
            # Parse the application areas to check the fix
            app_areas = result.get('application_areas', '[]')
            typical_cases = result.get('typical_use_cases', '[]')
            
            if app_areas == '["walls"]' and typical_cases == '["walls"]':
                print("🎉 SUCCESS: Application extraction fix working correctly!")
                print("   ✅ Shows ['walls'] instead of generic applications")
                print("   ✅ Correctly extracted from specifications: 'Applications: Wall'")
                print("   ✅ No longer includes incorrect 'floors' for wall-only product")
                return True
            else:
                print("❌ ISSUE: Applications still showing incorrect values")
                print(f"   Expected: ['walls']")
                print(f"   Got application_areas: {app_areas}")
                print(f"   Got typical_use_cases: {typical_cases}")
                return False
        else:
            print("❌ Extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_fix()
    if success:
        print("\n🎯 RECOMMENDATION: The fix is working correctly!")
        print("   Next steps:")
        print("   1. Test in dashboard by searching for SKU 485020")
        print("   2. Verify dashboard shows 'Applications: Wall' only")
        print("   3. Confirm no 'floors' listed for this wall-only tile")
    else:
        print("\n❌ ISSUE: Fix needs additional debugging")