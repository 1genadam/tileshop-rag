#!/usr/bin/env python3
"""
Test curl-based price extraction for SKU 485000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from curl_scraper import scrape_product_with_curl

def test_curl_price_extraction():
    print("🧪 Testing Curl-Based Price Extraction for SKU 485000")
    print("=" * 60)
    
    url = "https://www.tileshop.com/products/laura-park-bespoke-white-ceramic-wall-tile-256-x-10-in-485000"
    
    try:
        print(f"🔍 Using curl scraper for: {url}")
        
        # Use the proven curl-based approach
        result = scrape_product_with_curl(url)
        
        if result:
            print("✅ Curl scraping completed successfully")
            print(f"💾 Results:")
            print(f"   SKU: {result.get('sku', 'N/A')}")
            print(f"   Price per box: {result.get('price_per_box', 'N/A')}")
            print(f"   Coverage: {result.get('coverage', 'N/A')}")
            print(f"   Price per sqft: {result.get('price_per_sqft', 'N/A')}")
            print(f"   Color: {result.get('color', 'N/A')}")
            
            # Check if price was displayed or calculated
            price_box = result.get('price_per_box')
            coverage = result.get('coverage')
            price_sqft = result.get('price_per_sqft')
            
            if price_box and coverage and price_sqft:
                import re
                try:
                    price_num = float(str(price_box).replace('$', ''))
                    coverage_match = re.search(r'([0-9]+\.?[0-9]*)', str(coverage))
                    if coverage_match:
                        coverage_num = float(coverage_match.group(1))
                        calculated = round(price_num / coverage_num, 2)
                        
                        print(f"\n📊 Price Analysis:")
                        print(f"   Website price per box: ${price_num}")
                        print(f"   Website coverage: {coverage_num} sq ft")
                        print(f"   Mathematical calculation: ${price_num} ÷ {coverage_num} = ${calculated}")
                        print(f"   Extracted price per sqft: ${price_sqft}")
                        
                        if abs(float(price_sqft) - calculated) < 0.01:
                            print(f"   ✅ Price source: CALCULATED - no displayed price found")
                        else:
                            print(f"   ✅ Price source: DISPLAYED from website")
                            print(f"   📝 Note: Website shows different price than calculation")
                except Exception as e:
                    print(f"   ❌ Unable to analyze pricing: {e}")
        else:
            print("❌ Curl scraping failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_curl_price_extraction()