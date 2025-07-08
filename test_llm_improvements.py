#!/usr/bin/env python3
"""
Test LLM-based improvements on specific products
"""

import os
import sys
import json
import time
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_specification_extractor import EnhancedSpecificationExtractor
from enhanced_categorization_system import EnhancedCategorizer

def test_product_improvements(url):
    """Test a specific product URL with improved LLM-based detection"""
    
    print(f"\n🧪 Testing LLM improvements on: {url}")
    print("=" * 80)
    
    # Get SKU from URL
    sku = url.split('-')[-1] if '-' in url else url.split('/')[-1]
    # Try with and without leading zero
    sku_padded = sku.zfill(6) if len(sku) == 5 else sku
    print(f"SKU: {sku} (also trying: {sku_padded})")
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port='5432',
            user='postgres',
            database='postgres'
        )
        cursor = conn.cursor()
        
        # Check if product exists in database
        cursor.execute("""
            SELECT url, title, specifications, category_data, material_type, product_category
            FROM product_data 
            WHERE url = %s OR sku = %s OR sku = %s
            ORDER BY created_at DESC 
            LIMIT 1
        """, (url, sku, sku_padded))
        
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Product not found in database for URL: {url}")
            return
        
        db_url, title, specifications, category_data, material_type, product_category = result
        
        print(f"✅ Found product: {title}")
        print(f"Current material_type: {material_type}")
        print(f"Current product_category: {product_category}")
        
        # Parse specifications
        if isinstance(specifications, str):
            try:
                specs = json.loads(specifications)
            except:
                specs = {}
        else:
            specs = specifications or {}
        
        print(f"Current specifications: {specs}")
        
        # Test enhanced categorization system
        print("\n🔍 Testing Enhanced Categorization...")
        categorizer = EnhancedCategorizer()
        
        # Create product data for testing
        product_data = {
            'title': title,
            'specifications': specs,
            'url': db_url
        }
        
        # Test material type detection
        detected_material = categorizer.extract_material_type(product_data)
        print(f"🔍 LLM-detected material type: {detected_material}")
        
        # Test specification extraction with LLM
        print("\n🔍 Testing Enhanced Specification Extraction...")
        extractor = EnhancedSpecificationExtractor()
        
        # We need the HTML content to test specification extraction
        # For now, just test with the title
        enhanced_specs = extractor._detect_category_with_llm(title, "")
        print(f"🔍 LLM-detected category: {enhanced_specs}")
        
        # Summary
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"{'Field':<20} {'Current':<15} {'LLM-Detected':<15} {'Status'}")
        print("-" * 65)
        
        material_status = "✅ IMPROVED" if detected_material and detected_material != material_type else "🔄 SAME" if detected_material == material_type else "❌ NO CHANGE"
        category_status = "✅ IMPROVED" if enhanced_specs and enhanced_specs != product_category else "🔄 SAME" if enhanced_specs == product_category else "❌ NO CHANGE"
        
        print(f"{'Material Type':<20} {str(material_type):<15} {str(detected_material):<15} {material_status}")
        print(f"{'Product Category':<20} {str(product_category):<15} {str(enhanced_specs):<15} {category_status}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing product: {e}")

def main():
    """Test specific products with LLM improvements"""
    
    # Test the 5 problematic SKUs mentioned in the session
    test_urls = [
        "https://www.tileshop.com/products/superior-excel-standard-white-sanded-grout-25lb-52271",
        "https://www.tileshop.com/products/ardex-x5-tile-and-stone-gray-thinset-mortar-40-lbs-12531", 
        "https://www.tileshop.com/products/primo-euro-style-riveted-trowel-350142",
        "https://www.tileshop.com/products/superior-whisper-grey-100-silicone-caulk-105oz-51801",
        "https://www.tileshop.com/products/wedi-board-3-ft-x-5-ft-x-0-5-in-348940"
    ]
    
    if len(sys.argv) > 1:
        # Test specific URL from command line
        url = sys.argv[1]
        test_product_improvements(url)
    else:
        # Test all problematic products
        print("🧪 Testing LLM improvements on all problematic products...")
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n{'='*20} TEST {i}/5 {'='*20}")
            test_product_improvements(url)
            
            if i < len(test_urls):
                print(f"\n⏳ Waiting 2 seconds before next test...")
                time.sleep(2)

if __name__ == "__main__":
    main()