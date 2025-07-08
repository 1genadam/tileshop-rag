#!/usr/bin/env python3
"""
Test data quality fixes for the specific issues mentioned
"""

import sys
import json
from enhanced_specification_extractor import EnhancedSpecificationExtractor
from enhanced_categorization_system import EnhancedCategorizer

def test_data_cleaning():
    """Test the data cleaning and material type detection"""
    
    # Test data based on the problematic URL
    test_product_data = {
        'title': 'Marmi Imperiali Domitia Porcelain Wall and Floor Tile - 12 in.',
        'description': 'Beautiful porcelain tile for walls and floors',
        'url': 'https://www.tileshop.com/products/marmi-imperiali-domitia-porcelain-wall-and-floor-tile-12-in-684286',
        'specifications': {
            'texture': '_Detail:Asset_Grid_All_V2"}',
            'style': '/>',
            'installation_method': '-care/installation/tools">',
            'pattern': 'by pairing this tile with the Marmi Imperiali Aurelia or Zenobia tile (or use all three for a unique',
            'material': 'Material',
            'thickness': '10mm'
        }
    }
    
    print("🧪 Testing Data Quality Fixes")
    print("=" * 50)
    
    # Test 1: Material Type Detection
    print("\n1. Testing Material Type Detection:")
    categorizer = EnhancedCategorizer()
    category_info = categorizer.categorize_product(test_product_data)
    
    print(f"   Title: {test_product_data['title']}")
    print(f"   Should detect: Porcelain")
    print(f"   Primary Category: {category_info.primary_category}")
    print(f"   Subcategory: {category_info.subcategory}")
    print(f"   Product Type: {category_info.product_type}")
    
    # Test 2: Specification Cleaning
    print("\n2. Testing Specification Cleaning:")
    spec_extractor = EnhancedSpecificationExtractor()
    
    print("   Original corrupted data:")
    for field, value in test_product_data['specifications'].items():
        print(f"     {field}: {value}")
    
    # Test the cleaning function directly
    cleaned_specs = spec_extractor._clean_specifications(test_product_data['specifications'])
    
    print("\n   After cleaning:")
    for field, value in cleaned_specs.items():
        print(f"     {field}: {value}")
    
    # Test 3: Pattern Detection (Yes/No logic)
    print("\n3. Testing Pattern Detection:")
    pattern_text = test_product_data['specifications']['pattern']
    print(f"   Original: {pattern_text}")
    
    # Check if pattern detection logic exists
    has_pattern = 'pattern' in pattern_text.lower()
    pattern_result = 'Yes' if has_pattern else 'No'
    print(f"   Should be: Yes (mentions pairing/pattern)")
    print(f"   Detected: {pattern_result}")
    
    # Test 4: Product Category Detection
    print("\n4. Testing Product Category Detection:")
    title = test_product_data['title']
    print(f"   Title: {title}")
    print(f"   Should detect: tile")
    
    # Check if 'tile' is detected in title
    category_detected = 'tile' in title.lower()
    print(f"   'Tile' in title: {category_detected}")
    print(f"   Primary category: {category_info.primary_category}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    
    return {
        'material_type_detected': category_info.subcategory,
        'corrupted_data_cleaned': len(cleaned_specs) < len(test_product_data['specifications']),
        'pattern_logic_works': pattern_result == 'Yes',
        'category_detected': category_detected
    }

if __name__ == "__main__":
    results = test_data_cleaning()
    print(f"\n📊 Summary: {results}")