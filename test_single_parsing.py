#!/usr/bin/env python3
"""
Test script to validate parsing fixes on a single URL
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tileshop_learner import crawl_page_with_tabs, extract_product_data

def test_single_url_parsing():
    """Test parsing on SKU 351300 to validate the fix"""
    
    # Test URL - SKU 351300 (installation tool that was missing data)
    test_url = "https://www.tileshop.com/products/best-of-everything-lippage-red-wedge-250-pieces-per-bag-351300"
    
    print(f"🧪 Testing parsing fix on: {test_url}")
    print("=" * 80)
    
    try:
        # Step 1: Crawl with crawl4ai
        print("Step 1: Crawling with crawl4ai...")
        crawl_results = crawl_page_with_tabs(test_url)
        
        if not crawl_results:
            print("❌ Crawl failed - no results returned")
            return False
        
        print(f"✅ Crawl completed. Tabs found: {list(crawl_results.keys())}")
        
        # Step 2: Extract product data
        print("\nStep 2: Extracting product data...")
        product_data = extract_product_data(crawl_results, test_url)
        
        if not product_data:
            print("❌ Product data extraction failed")
            return False
        
        # Step 3: Validate key fields
        print("\nStep 3: Validating extracted data...")
        print("=" * 50)
        
        # Check critical fields
        fields_to_check = ['sku', 'title', 'brand', 'price_per_piece', 'price_per_box', 'description']
        success_count = 0
        
        for field in fields_to_check:
            value = product_data.get(field)
            if value and value != 'The Tile Shop - High Quality Floor & Wall Tile':
                print(f"✅ {field}: {value}")
                success_count += 1
            else:
                print(f"❌ {field}: Missing or generic")
        
        # Calculate success rate
        success_rate = (success_count / len(fields_to_check)) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}% ({success_count}/{len(fields_to_check)} fields)")
        
        # Show all extracted data
        print("\n📋 Complete extracted data:")
        print("-" * 50)
        for key, value in product_data.items():
            if value:
                print(f"{key}: {value}")
        
        return success_rate > 50  # Consider >50% success as improvement
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing parsing system fixes...")
    print("Target: SKU 351300 - Best of Everything Wedge and Lippage Leveling System")
    print()
    
    success = test_single_url_parsing()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TEST PASSED - Parsing improvements validated!")
        print("Ready to apply fixes to full system")
    else:
        print("❌ TEST FAILED - Need to investigate further")
        print("Check crawl4ai service and parsing logic")