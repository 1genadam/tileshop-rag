#!/usr/bin/env python3
"""
Test LLM improvements on multiple diverse products
"""

import os
import sys
import json
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_product_parsing(url, expected_results=None):
    """Test parsing a single product with LLM improvements"""
    
    print(f"\n🧪 Testing: {url}")
    print("=" * 120)
    
    # Set the API key environment variable
    env = os.environ.copy()
    env['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', 'your-api-key-here')
    
    # Extract SKU from URL
    sku = url.split('-')[-1] if '-' in url else url.split('/')[-1]
    
    # Delete existing product to force re-parsing
    print("1. Clearing existing data...")
    delete_cmd = [
        'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-c',
        f"DELETE FROM product_data WHERE url = '{url}' OR sku = '{sku}' OR sku = '{sku.zfill(6)}';"
    ]
    
    try:
        subprocess.run(delete_cmd, capture_output=True, text=True, check=True)
        print("   ✅ Cleared from database")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Clear failed: {e}")
    
    # Run parsing
    print("2. Running LLM-enhanced parsing...")
    
    parse_cmd = ['python', 'curl_scraper.py', url]
    
    try:
        result = subprocess.run(parse_cmd, capture_output=True, text=True, env=env, timeout=180)
        
        # Extract key information from parsing output
        parsing_success = "✅ Successfully processed" in result.stdout
        llm_material_detected = "Material type detected with LLM:" in result.stdout or "Material type corrected:" in result.stdout
        llm_category_detected = "Category detected with LLM:" in result.stdout
        
        print(f"   Parsing Success: {'✅' if parsing_success else '❌'}")
        print(f"   LLM Material Detection: {'✅' if llm_material_detected else '❌'}")
        print(f"   LLM Category Detection: {'✅' if llm_category_detected else '❌'}")
        
        if result.stderr and "Error" in result.stderr:
            print(f"   ⚠️ Parsing warnings: {result.stderr[:200]}...")
        
    except subprocess.TimeoutExpired:
        print("   ❌ Parsing timed out")
        return None
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Parsing failed: {e}")
        return None
    
    # Check results in database
    print("3. Analyzing results...")
    
    check_cmd = [
        'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-t', '-c',
        f"""SELECT title, brand, material_type, product_category, category, subcategory 
            FROM product_data 
            WHERE url = '{url}' OR sku = '{sku}' OR sku = '{sku.zfill(6)}' 
            LIMIT 1;"""
    ]
    
    try:
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, check=True)
        output = check_result.stdout.strip()
        
        if not output or output == '(0 rows)':
            print("   ❌ Product not found in database")
            return None
        
        # Parse the result
        parts = [p.strip() for p in output.split('|')]
        if len(parts) >= 6:
            title = parts[0]
            brand = parts[1] if parts[1] else 'Not detected'
            material_type = parts[2] if parts[2] else 'Not detected'
            product_category = parts[3] if parts[3] else 'Not detected'
            category = parts[4] if parts[4] else 'Not detected'
            subcategory = parts[5] if parts[5] else 'Not detected'
            
            results = {
                'title': title,
                'brand': brand,
                'material_type': material_type,
                'product_category': product_category,
                'category': category,
                'subcategory': subcategory
            }
            
            print(f"   📄 Title: {title}")
            print(f"   🏢 Brand: {brand}")
            print(f"   🧱 Material Type: {material_type}")
            print(f"   📦 Product Category: {product_category}")
            print(f"   🗂️ Category: {category}")
            print(f"   📂 Subcategory: {subcategory}")
            
            # Validate against expectations if provided
            if expected_results:
                print("\n   📊 Validation:")
                for field, expected in expected_results.items():
                    actual = results.get(field, 'Not detected')
                    if expected.lower() in actual.lower() or actual.lower() in expected.lower():
                        print(f"      ✅ {field}: Expected '{expected}' → Got '{actual}'")
                    else:
                        print(f"      ❌ {field}: Expected '{expected}' → Got '{actual}'")
            
            return results
            
        else:
            print(f"   ❌ Unexpected database result format: {output}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Database check failed: {e}")
        return None

def main():
    """Test multiple products with LLM improvements"""
    
    # Test products with expected results
    test_products = [
        {
            'url': 'https://www.tileshop.com/products/superior-premium-gold-stone-sealer-pint-220434',
            'expected': {
                'brand': 'Superior',
                'material_type': 'sealer',  # Chemical sealer product
                'product_category': 'Sealer',
                'category': 'care_maintenance'
            }
        },
        {
            'url': 'https://www.tileshop.com/products/goboard-pro-sealant-20-oz-350051',
            'expected': {
                'brand': 'GOboard',
                'material_type': 'silicone',  # Sealant product
                'product_category': 'Sealer',
                'category': 'installation_materials'
            }
        },
        {
            'url': 'https://www.tileshop.com/products/ardex-t-7-ceramic-tile-sponge-12506',
            'expected': {
                'brand': 'Ardex',
                'material_type': 'synthetic',  # Sponge material
                'product_category': 'Tool',
                'category': 'tools'
            }
        },
        {
            'url': 'https://www.tileshop.com/products/goboard-backer-board-4-ft-x-8-ft-x-%C2%BD-in-350067',
            'expected': {
                'brand': 'GOboard',
                'material_type': 'polystyrene',  # Foam board substrate
                'product_category': 'Substrate',
                'category': 'installation_materials'
            }
        },
        {
            'url': 'https://www.tileshop.com/products/wedi-screw-and-washer-fastener-kit-349133',
            'expected': {
                'brand': 'Wedi',
                'material_type': 'metal',  # Screws and washers
                'product_category': 'Tool',
                'category': 'tools'
            }
        }
    ]
    
    print("🔬 Testing LLM-based detection on 5 diverse products")
    print("Testing: Category, Material Type, Brand, and Product Category detection")
    print("=" * 120)
    
    results = []
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{'🧪 TEST ' + str(i) + '/5 ':=^120}")
        
        result = test_product_parsing(product['url'], product['expected'])
        
        if result:
            results.append({
                'url': product['url'],
                'expected': product['expected'],
                'actual': result
            })
        
        # Add delay between tests to avoid overwhelming the system
        if i < len(test_products):
            print("\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'📊 SUMMARY ':=^120}")
    
    total_tests = len(test_products)
    successful_parses = len(results)
    
    print(f"Successful Parses: {successful_parses}/{total_tests}")
    
    if results:
        print("\n🔍 Field Accuracy Analysis:")
        
        fields = ['brand', 'material_type', 'product_category', 'category']
        field_accuracy = {}
        
        for field in fields:
            correct = 0
            total = 0
            
            for result in results:
                if field in result['expected']:
                    total += 1
                    expected = result['expected'][field].lower()
                    actual = result['actual'].get(field, '').lower()
                    
                    if expected in actual or actual in expected:
                        correct += 1
            
            if total > 0:
                accuracy = (correct / total) * 100
                field_accuracy[field] = accuracy
                print(f"   {field.replace('_', ' ').title()}: {correct}/{total} ({accuracy:.1f}%)")
        
        overall_accuracy = sum(field_accuracy.values()) / len(field_accuracy) if field_accuracy else 0
        print(f"\n🎯 Overall Detection Accuracy: {overall_accuracy:.1f}%")
        
        if overall_accuracy >= 80:
            print("✅ EXCELLENT: LLM detection is working very well!")
        elif overall_accuracy >= 60:
            print("✅ GOOD: LLM detection is working well with room for improvement")
        else:
            print("⚠️ NEEDS WORK: LLM detection needs improvement")
    
    print("\n" + "=" * 120)

if __name__ == "__main__":
    main()