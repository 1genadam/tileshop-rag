#!/usr/bin/env python3
"""
Test SKU 683861 processing with enhanced field extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tileshop_learner import save_to_database
from curl_scraper import scrape_product_with_curl

def test_sku_683861():
    url = 'https://www.tileshop.com/products/morris-&-co-pure-net-brick-porcelain-wall-and-floor-tile-13-x-13-in-683861'
    
    print('🔍 Testing SKU 683861 processing...')
    print('=' * 60)
    
    # Use enhanced curl scraper with tab support
    print('\n📋 Processing product data with enhanced curl scraper...')
    product_data = scrape_product_with_curl(url)
    
    print('\n📊 EXTRACTED DATA:')
    print(f'  SKU: {product_data.get("sku", "NOT FOUND")}')
    print(f'  Title: {product_data.get("title", "NOT FOUND")}')
    print(f'  Price per sqft: {product_data.get("price_per_sqft", "NOT FOUND")}')
    print(f'  Color: {product_data.get("color", "NOT FOUND")}')
    print(f'  Category: {product_data.get("category", "NOT FOUND")}')
    print(f'  Resources: {product_data.get("resources", "NOT FOUND")}')
    
    # Save to database (force save to ensure resources are updated)
    if product_data:
        print('\n💾 Force saving updated product data...')
        # Create minimal crawl_results for save function
        crawl_results = {'main': {'html': '', 'markdown': ''}}
        save_to_database(product_data, crawl_results)
    
    print('\n✅ PROCESSING COMPLETE')
    
    return product_data

if __name__ == "__main__":
    test_sku_683861()