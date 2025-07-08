#!/usr/bin/env python3
"""
Test that LLM improvements are integrated into the main parsing pipeline
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_integrated_parsing():
    """Test that the parsing pipeline now includes LLM improvements"""
    
    # Test URL - the thinset product that should get corrected from "natural stone" to "cement"
    test_url = "https://www.tileshop.com/products/ardex-x5-tile-and-stone-gray-thinset-mortar-40-lbs-12531"
    
    print("🧪 Testing integrated LLM improvements in parsing pipeline...")
    print(f"Target: {test_url}")
    print("=" * 80)
    
    # Set the API key environment variable
    env = os.environ.copy()
    env['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', 'your-api-key-here')
    
    # First, delete the existing product to force re-parsing
    print("1. Deleting existing product from database...")
    delete_cmd = [
        'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-c',
        f"DELETE FROM product_data WHERE url = '{test_url}' OR sku = '12531' OR sku = '012531';"
    ]
    
    try:
        subprocess.run(delete_cmd, capture_output=True, text=True, check=True)
        print("   ✅ Product deleted from database")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Delete failed: {e}")
    
    # Now run the parsing using the curl scraper
    print("\\n2. Running integrated parsing with LLM improvements...")
    
    parse_cmd = [
        'python', 'curl_scraper.py', test_url
    ]
    
    try:
        result = subprocess.run(parse_cmd, capture_output=True, text=True, env=env, timeout=300)
        
        print("PARSING OUTPUT:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\\nERRORS:")
            print("-" * 40)
            print(result.stderr)
        
        # Check the result in the database
        print("\\n3. Checking parsed result in database...")
        
        check_cmd = [
            'docker', 'exec', 'relational_db', 'psql', '-U', 'postgres', '-d', 'postgres', '-t', '-c',
            f"SELECT title, material_type, product_category FROM product_data WHERE url = '{test_url}' OR sku = '12531' OR sku = '012531' LIMIT 1;"
        ]
        
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, check=True)
        output = check_result.stdout.strip()
        
        if not output or output == '(0 rows)':
            print("   ❌ Product not found in database after parsing")
            return False
        
        # Parse the result
        parts = output.split('|')
        if len(parts) >= 3:
            title = parts[0].strip()
            material_type = parts[1].strip()
            product_category = parts[2].strip()
            
            print(f"   ✅ Product found: {title}")
            print(f"   Material Type: {material_type}")
            print(f"   Product Category: {product_category}")
            
            # Verify the improvement
            if material_type == 'cement':
                print("   🎉 SUCCESS: Material type correctly detected as 'cement' (was 'natural stone')")
                return True
            elif material_type == 'natural stone':
                print("   ❌ FAILED: Material type still incorrectly detected as 'natural stone'")
                return False
            else:
                print(f"   ⚠️ UNEXPECTED: Material type is '{material_type}'")
                return False
        else:
            print(f"   ❌ Unexpected database result format: {output}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Parsing timed out after 5 minutes")
        return False
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Parsing failed: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False

if __name__ == "__main__":
    success = test_integrated_parsing()
    
    if success:
        print("\\n✅ INTEGRATION TEST PASSED: LLM improvements are working in the parsing pipeline!")
    else:
        print("\\n❌ INTEGRATION TEST FAILED: LLM improvements are not working properly")
    
    sys.exit(0 if success else 1)