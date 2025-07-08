#!/usr/bin/env python3
"""
Test script to debug SKU 684287 extraction issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_specification_extractor import EnhancedSpecificationExtractor
import requests
import re

def test_sku_684287_extraction():
    """Test the specification extraction for SKU 684287"""
    
    # Create extractor instance
    extractor = EnhancedSpecificationExtractor()
    
    # Test URL for SKU 684287
    test_url = "https://www.tileshop.com/product/684287"
    
    print(f"Testing specification extraction for SKU 684287")
    print(f"URL: {test_url}")
    print("=" * 60)
    
    try:
        # Fetch the page
        response = requests.get(test_url)
        response.raise_for_status()
        html_content = response.text
        
        print(f"Successfully fetched page (length: {len(html_content)} characters)")
        
        # Extract product title from HTML
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        product_title = ""
        if title_match:
            product_title = title_match.group(1).strip()
            product_title = product_title.replace(' - The Tile Shop', '')
        
        print(f"Product Title: {product_title}")
        
        # Test WITHOUT product_title (current broken behavior)
        print("\n--- Testing WITHOUT product_title (current behavior) ---")
        specs_without_title = extractor.extract_specifications(html_content, "tile")
        print(f"Extracted fields: {list(specs_without_title.keys())}")
        print(f"Edge Type: {specs_without_title.get('edge_type', 'NOT FOUND')}")
        print(f"Product Category: {specs_without_title.get('product_category', 'NOT FOUND')}")
        
        # Test WITH product_title (fixed behavior)
        print("\n--- Testing WITH product_title (fixed behavior) ---")
        specs_with_title = extractor.extract_specifications(html_content, "tile", product_title)
        print(f"Extracted fields: {list(specs_with_title.keys())}")
        print(f"Edge Type: {specs_with_title.get('edge_type', 'NOT FOUND')}")
        print(f"Product Category: {specs_with_title.get('product_category', 'NOT FOUND')}")
        
        # Check for specific patterns that should match
        print("\n--- Checking for specific patterns ---")
        
        # Check for edge type pattern
        edge_pattern = r'"PDPInfo_EdgeType","Value":"([^"]+)"'
        edge_match = re.search(edge_pattern, html_content)
        if edge_match:
            print(f"Found edge type pattern: {edge_match.group(1)}")
        else:
            print("Edge type pattern NOT found")
            
        # Check for other edge patterns
        other_patterns = [
            r'Edge Type[:\s]*([^<\n,]+)',
            r'"edgeType"[:\s]*"([^"]+)"',
            r'Edge[:\s]*([^<\n,]+)',
            r'Rectified[:\s]*(Yes|No)'
        ]
        
        for pattern in other_patterns:
            match = re.search(pattern, html_content)
            if match:
                print(f"Found alternative edge pattern '{pattern}': {match.group(1)}")
        
        # Save HTML for manual inspection
        with open('/tmp/sku_684287_debug.html', 'w') as f:
            f.write(html_content)
        print(f"\nHTML saved to /tmp/sku_684287_debug.html for manual inspection")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sku_684287_extraction()