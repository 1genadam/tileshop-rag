#!/usr/bin/env python3
"""
Simple test of LLM improvements using Docker exec
"""

import os
import sys
import json
import subprocess

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_specification_extractor import EnhancedSpecificationExtractor
from enhanced_categorization_system import EnhancedCategorizer

def get_product_from_db(sku):
    """Get product from database using docker exec"""
    
    # Try with and without leading zero
    sku_padded = sku.zfill(6) if len(sku) == 5 else sku
    
    cmd = [
        'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-t', '-c',
        f"SELECT title, specifications, material_type, product_category FROM product_data WHERE sku = '{sku}' OR sku = '{sku_padded}' LIMIT 1;"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        if not output or output == '(0 rows)':
            return None
            
        # Parse the result
        parts = output.split('|')
        if len(parts) >= 4:
            title = parts[0].strip()
            specifications = parts[1].strip()
            material_type = parts[2].strip() if parts[2].strip() else None
            product_category = parts[3].strip() if parts[3].strip() else None
            
            return {
                'title': title,
                'specifications': specifications,
                'material_type': material_type,
                'product_category': product_category
            }
    except subprocess.CalledProcessError as e:
        print(f"Database error: {e}")
        return None
    
    return None

def test_product_improvements(url):
    """Test a specific product URL with improved LLM-based detection"""
    
    print(f"\n🧪 Testing LLM improvements on: {url}")
    print("=" * 80)
    
    # Get SKU from URL
    sku = url.split('-')[-1] if '-' in url else url.split('/')[-1]
    print(f"SKU: {sku}")
    
    # Get product from database
    product = get_product_from_db(sku)
    
    if not product:
        print(f"❌ Product not found in database for SKU: {sku}")
        return
    
    title = product['title']
    specifications = product['specifications']
    material_type = product['material_type']
    product_category = product['product_category']
    
    print(f"✅ Found product: {title}")
    print(f"Current material_type: {material_type}")
    print(f"Current product_category: {product_category}")
    
    # Parse specifications
    try:
        if specifications and specifications not in ['', '{}']:
            specs = json.loads(specifications)
        else:
            specs = {}
    except:
        specs = {}
    
    print(f"Current specifications: {specs}")
    
    # Test enhanced categorization system
    print("\n🔍 Testing Enhanced Categorization...")
    categorizer = EnhancedCategorizer()
    
    # Create product data for testing
    product_data = {
        'title': title,
        'specifications': specs
    }
    
    # Test material type detection
    detected_material = categorizer.extract_material_type(product_data)
    print(f"🔍 LLM-detected material type: {detected_material}")
    
    # Test specification extraction with LLM
    print("\n🔍 Testing Enhanced Specification Extraction...")
    extractor = EnhancedSpecificationExtractor()
    
    # Test category detection
    enhanced_category = extractor._detect_category_with_llm(title, "")
    print(f"🔍 LLM-detected category: {enhanced_category}")
    
    # Summary
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"{'Field':<20} {'Current':<15} {'LLM-Detected':<15} {'Status'}")
    print("-" * 65)
    
    material_status = "✅ IMPROVED" if detected_material and detected_material != material_type else "🔄 SAME" if detected_material == material_type else "❌ NO CHANGE"
    category_status = "✅ IMPROVED" if enhanced_category and enhanced_category != product_category else "🔄 SAME" if enhanced_category == product_category else "❌ NO CHANGE"
    
    print(f"{'Material Type':<20} {str(material_type):<15} {str(detected_material):<15} {material_status}")
    print(f"{'Product Category':<20} {str(product_category):<15} {str(enhanced_category):<15} {category_status}")

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

if __name__ == "__main__":
    main()