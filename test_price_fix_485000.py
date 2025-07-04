#!/usr/bin/env python3
"""
Test price extraction fix for SKU 485000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tileshop_learner import crawl_page_with_tabs, extract_product_data

def test_price_extraction_fix():
    print("🧪 Testing Price Extraction Fix for SKU 485000")
    print("=" * 60)
    
    url = "https://www.tileshop.com/products/laura-park-bespoke-white-ceramic-wall-tile-256-x-10-in-485000"
    
    try:
        print(f"🔍 Crawling URL: {url}")
        
        # Step 1: Crawl the page with all tabs
        crawl_results = crawl_page_with_tabs(url)
        
        if not crawl_results:
            print("❌ Failed to crawl page")
            return
            
        print("✅ Successfully crawled page with tabs")
        
        # Step 2: Extract product data with enhanced field extraction
        print("🔧 Extracting product data with enhanced logic...")
        product_data = extract_product_data(crawl_results, url)
        
        if product_data:
            print("✅ Product data extracted successfully")
            print(f"💾 Results:")
            print(f"   SKU: {product_data.get('sku', 'N/A')}")
            print(f"   Price per box: {product_data.get('price_per_box', 'N/A')}")
            print(f"   Coverage: {product_data.get('coverage', 'N/A')}")
            print(f"   Price per sqft: {product_data.get('price_per_sqft', 'N/A')}")
            print(f"   Color: {product_data.get('color', 'N/A')}")
            
            # Check if price was displayed or calculated
            price_box = product_data.get('price_per_box')
            coverage = product_data.get('coverage')
            price_sqft = product_data.get('price_per_sqft')
            
            if price_box and coverage and price_sqft:
                import re
                try:
                    price_num = float(str(price_box).replace('$', ''))
                    coverage_match = re.search(r'([0-9]+\.?[0-9]*)', str(coverage))
                    if coverage_match:
                        coverage_num = float(coverage_match.group(1))
                        calculated = round(price_num / coverage_num, 2)
                        
                        if abs(float(price_sqft) - calculated) < 0.01:
                            print(f"📊 Price source: CALCULATED (${price_num} ÷ {coverage_num} = ${calculated})")
                            print("   ✅ This means no displayed price was found on website")
                        else:
                            print(f"📊 Price source: DISPLAYED from website (${price_sqft})")
                            print(f"   📝 Note: Different from calculated (${calculated})")
                except:
                    print("📊 Unable to determine price source")
        else:
            print("❌ Failed to extract product data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_price_extraction_fix()