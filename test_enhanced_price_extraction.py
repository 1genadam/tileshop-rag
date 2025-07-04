#!/usr/bin/env python3
"""
Test the enhanced price extraction logic for SKU 485000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tileshop_learner import scrape_and_save_product

def test_enhanced_price_extraction():
    print("🧪 Testing Enhanced Price Extraction for SKU 485000")
    print("=" * 60)
    
    url = "https://www.tileshop.com/products/laura-park-bespoke-white-ceramic-wall-tile-256-x-10-in-485000"
    
    try:
        print(f"🔍 Scraping: {url}")
        
        # This will use the enhanced field extraction logic
        result = scrape_and_save_product(url)
        
        if result:
            print("✅ Scraping completed successfully")
            
            # Query the database to see what was extracted
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
                SELECT sku, price_per_box, coverage, price_per_sqft, scraped_at
                FROM product_data 
                WHERE sku = '485000'
                ORDER BY scraped_at DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result:
                sku, price_box, coverage, price_sqft, scraped_at = result
                print(f"💾 Database Results:")
                print(f"   SKU: {sku}")
                print(f"   Price per box: {price_box}")
                print(f"   Coverage: {coverage}")
                print(f"   Price per sqft: {price_sqft}")
                print(f"   Scraped at: {scraped_at}")
                
                # Check if this is displayed or calculated
                if price_box and coverage:
                    import re
                    price_num = float(str(price_box).replace('$', ''))
                    coverage_match = re.search(r'([0-9]+\.?[0-9]*)', str(coverage))
                    if coverage_match:
                        coverage_num = float(coverage_match.group(1))
                        calculated = round(price_num / coverage_num, 2)
                        
                        if abs(float(price_sqft) - calculated) < 0.01:
                            print(f"📊 Price source: CALCULATED (${price_num} ÷ {coverage_num} = ${calculated})")
                        else:
                            print(f"📊 Price source: DISPLAYED (extracted from website)")
            
            cursor.close()
            conn.close()
            
        else:
            print("❌ Scraping failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_price_extraction()