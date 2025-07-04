#!/usr/bin/env python3
"""
Test SKU 485020 application field extraction from specifications tab
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from curl_scraper import scrape_product_with_curl

def test_application_extraction():
    print("🧪 Testing Application Field Extraction for SKU 485020")
    print("=" * 60)
    
    url = "https://www.tileshop.com/products/linewood-white-matte-ceramic-wall-tile-12-x-36-in-485020"
    
    try:
        print(f"🔍 Using curl scraper for: {url}")
        
        # Use the proven curl-based approach
        result = scrape_product_with_curl(url)
        
        if result:
            print("✅ Curl scraping completed successfully")
            print(f"💾 Results:")
            print(f"   SKU: {result.get('sku', 'N/A')}")
            print(f"   Application Areas: {result.get('application_areas', 'N/A')}")
            print(f"   Typical Use Cases: {result.get('typical_use_cases', 'N/A')}")
            print(f"   Product Type: {result.get('product_type', 'N/A')}")
            print(f"   Category: {result.get('category', 'N/A')}")
            print(f"   Subcategory: {result.get('subcategory', 'N/A')}")
            
            # Check current database entry
            print(f"\n🔍 Checking current database entry...")
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='postgres',
                user='postgres',
                password='postgres'
            )
            
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sku, typical_use_cases, application_areas, product_type
                FROM product_data 
                WHERE sku = '485020'
                ORDER BY scraped_at DESC
                LIMIT 1
            ''')
            
            db_result = cursor.fetchone()
            if db_result:
                sku, use_cases, app_areas, prod_type = db_result
                print(f"📊 Database Current Values:")
                print(f"   SKU: {sku}")
                print(f"   Typical Use Cases: {use_cases}")
                print(f"   Application Areas: {app_areas}")
                print(f"   Product Type: {prod_type}")
                
                # Parse the typical_use_cases JSON to see what's wrong
                import json
                try:
                    if use_cases:
                        parsed_cases = json.loads(use_cases)
                        print(f"   ❌ Issue: Shows {parsed_cases} but should be ['walls'] only")
                except:
                    print(f"   📝 Raw use cases: {use_cases}")
            else:
                print("   ❌ No database entry found for SKU 485020")
            
            cursor.close()
            conn.close()
        else:
            print("❌ Curl scraping failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_application_extraction()