#!/usr/bin/env python3
"""
Test SKU 485000 processing with enhanced field extraction fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tileshop_learner import save_to_database
from curl_scraper import scrape_product_with_curl

def test_sku_485000():
    url = 'https://www.tileshop.com/products/laura-park-bespoke-white-ceramic-wall-tile-256-x-10-in-485000'
    
    print('🔍 Testing SKU 485000 processing with FIXES...')
    print('=' * 60)
    
    # Use enhanced curl scraper with tab support
    print('\n📋 Processing product data with enhanced curl scraper...')
    product_data = scrape_product_with_curl(url)
    
    print('\n📊 EXTRACTED DATA:')
    print(f'  SKU: {product_data.get("sku", "NOT FOUND")}')
    print(f'  Title: {product_data.get("title", "NOT FOUND")}')
    print(f'  Price per box: {product_data.get("price_per_box", "NOT FOUND")}')
    print(f'  Coverage: {product_data.get("coverage", "NOT FOUND")}')
    print(f'  Price per sqft: {product_data.get("price_per_sqft", "NOT FOUND")}')
    print(f'  Color: {product_data.get("color", "NOT FOUND")}')
    print(f'  Category: {product_data.get("category", "NOT FOUND")}')
    print(f'  Resources: {product_data.get("resources", "NOT FOUND")}')
    
    print('\n🎯 ISSUE VERIFICATION:')
    
    # Check fixes
    issues_resolved = 0
    total_issues = 3
    
    # Issue 1: Price per sqft calculation
    if product_data.get('price_per_sqft'):
        print('  ✅ Price per sqft: FIXED')
        issues_resolved += 1
    else:
        print('  ❌ Price per sqft: STILL MISSING')
    
    # Issue 2: Color hex extraction
    color = product_data.get('color', '')
    if color and '#' in color and not any(char in color for char in ['\"', '/>', '}']):
        print('  ✅ Color parsing: FIXED')
        issues_resolved += 1
    else:
        print(f'  ❌ Color parsing: STILL BROKEN (got: {color})')
    
    # Issue 3: Resources extraction
    resources = product_data.get('resources', 'null')
    if resources and resources != 'null' and 'scene7.com' in resources:
        print('  ✅ Resources/PDF: FIXED')
        issues_resolved += 1
    else:
        print(f'  ❌ Resources/PDF: STILL MISSING (got: {resources})')
    
    print(f'\n📈 RESOLUTION SCORE: {issues_resolved}/{total_issues} issues fixed')
    
    # Save to database (force save to ensure updates persist)
    if product_data:
        print('\n💾 Force saving updated product data...')
        # Create minimal crawl_results for save function
        crawl_results = {'main': {'html': '', 'markdown': ''}}
        save_to_database(product_data, crawl_results)
    
    print('\n✅ PROCESSING COMPLETE')
    
    return product_data

if __name__ == "__main__":
    test_sku_485000()