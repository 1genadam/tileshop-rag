#!/usr/bin/env python3
"""
Comprehensive Data Extraction Audit for Tile Category
Analyzes SKU 485020 to identify missing specification fields and propose schema enhancements
"""

import sys
import os
import re
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from curl_scraper import scrape_product_with_curl

def audit_tile_data_extraction():
    print("🔍 COMPREHENSIVE TILE DATA EXTRACTION AUDIT")
    print("=" * 60)
    print("Target: SKU 485020 (Linewood White Matte Ceramic Wall Tile)")
    print()
    
    # Available fields from web analysis
    available_fields = {
        "Dimensions & Physical": {
            "Thickness": "8.7mm",
            "Box Quantity": "5", 
            "Box Weight": "45.5 lbs",
            "Coverage per Box": "14.74 sq. ft.",
            "Size": "12\" x 36\"",
        },
        "Design & Material": {
            "Material Type": "Ceramic",
            "Edge Type": "Rectified", 
            "Color": "Ivory, Taupe, White",
            "Finish": "Matte",
            "Shade Variation": "V3",
            "Number of Faces": "4",
            "Applications": "Wall",
            "Directional Layout": "Yes",
        },
        "Product Info": {
            "Country of Origin": "Spain",
            "Product Code": "485020",
        }
    }
    
    # Get current extraction
    print("📥 Testing current extraction...")
    url = "https://www.tileshop.com/products/linewood-white-matte-ceramic-wall-tile-12-x-36-in-485020"
    current_data = scrape_product_with_curl(url)
    
    if not current_data:
        print("❌ Failed to extract data")
        return
    
    print("✅ Current extraction completed")
    print()
    
    # Analyze gaps
    print("📊 DATA EXTRACTION AUDIT RESULTS")
    print("=" * 60)
    
    captured_fields = set()
    missing_fields = []
    
    for category, fields in available_fields.items():
        print(f"\n🏷️  {category.upper()}")
        print("-" * 40)
        
        for field_name, available_value in fields.items():
            # Check if we capture this field
            field_captured = False
            captured_value = None
            
            # Map field names to our schema
            field_mappings = {
                "Thickness": "thickness",
                "Box Quantity": "box_quantity", 
                "Box Weight": "box_weight",
                "Coverage per Box": "coverage",
                "Size": "size_shape",
                "Material Type": "material",
                "Edge Type": "edge_type",
                "Color": "color", 
                "Finish": "finish",
                "Shade Variation": "shade_variation",
                "Number of Faces": "number_of_faces",
                "Applications": "application_areas",
                "Directional Layout": "directional_layout",
                "Country of Origin": "country_of_origin",
                "Product Code": "sku",
            }
            
            mapped_field = field_mappings.get(field_name)
            if mapped_field and mapped_field in current_data:
                field_captured = True
                captured_value = current_data[mapped_field]
                captured_fields.add(mapped_field)
            
            # Check if value matches
            if field_captured:
                # Normalize for comparison
                available_norm = str(available_value).lower().replace('"', '').strip()
                captured_norm = str(captured_value).lower().strip()
                
                if available_norm in captured_norm or captured_norm in available_norm:
                    print(f"   ✅ {field_name}: {captured_value}")
                else:
                    print(f"   ⚠️  {field_name}: MISMATCH")
                    print(f"       Available: {available_value}")
                    print(f"       Captured:  {captured_value}")
            else:
                print(f"   ❌ {field_name}: NOT CAPTURED (Available: {available_value})")
                missing_fields.append({
                    "field": field_name,
                    "value": available_value,
                    "suggested_schema": mapped_field or field_name.lower().replace(" ", "_"),
                    "category": category
                })
    
    # Summary
    print(f"\n📈 AUDIT SUMMARY")
    print("=" * 60)
    
    total_available = sum(len(fields) for fields in available_fields.values())
    total_captured = len([f for f in captured_fields if f != 'sku'])  # Don't count SKU twice
    capture_rate = (total_captured / total_available) * 100
    
    print(f"Total Available Fields: {total_available}")
    print(f"Successfully Captured: {total_captured}")
    print(f"Capture Rate: {capture_rate:.1f}%")
    print(f"Missing Fields: {len(missing_fields)}")
    
    # Critical missing fields
    print(f"\n🚨 CRITICAL MISSING FIELDS")
    print("-" * 40)
    
    critical_fields = [
        "Box Quantity", "Box Weight", "Thickness", "Edge Type", 
        "Shade Variation", "Number of Faces", "Directional Layout", "Country of Origin"
    ]
    
    for missing in missing_fields:
        if missing["field"] in critical_fields:
            print(f"   ❌ {missing['field']}: {missing['value']}")
            print(f"      → Suggested schema field: {missing['suggested_schema']}")
    
    # Schema enhancement recommendations
    print(f"\n🔧 SCHEMA ENHANCEMENT RECOMMENDATIONS")
    print("-" * 40)
    
    recommended_fields = [
        ("thickness", "VARCHAR(20)", "Tile thickness (e.g., '8.7mm')"),
        ("box_quantity", "INTEGER", "Number of pieces per box"),
        ("box_weight", "VARCHAR(20)", "Weight of full box (e.g., '45.5 lbs')"),
        ("edge_type", "VARCHAR(50)", "Edge finish type (e.g., 'Rectified')"),
        ("shade_variation", "VARCHAR(10)", "Shade variation code (e.g., 'V3')"),
        ("number_of_faces", "INTEGER", "Number of distinct faces/patterns"),
        ("directional_layout", "BOOLEAN", "Whether tile has directional installation"),
        ("country_of_origin", "VARCHAR(100)", "Manufacturing country"),
        ("material_type", "VARCHAR(50)", "Specific material type (vs generic 'material')"),
    ]
    
    print("SQL to add missing fields:")
    for field, data_type, description in recommended_fields:
        print(f"   ALTER TABLE product_data ADD COLUMN {field} {data_type}; -- {description}")
    
    # Auto-extraction logic recommendations
    print(f"\n🤖 AUTO-EXTRACTION LOGIC ENHANCEMENTS")
    print("-" * 40)
    
    extraction_patterns = {
        "thickness": [r'Thickness[:\s]*([0-9.]+\s*mm)', r'"thickness"[:\s]*"([^"]+)"'],
        "box_quantity": [r'Box Quantity[:\s]*([0-9]+)', r'"boxQuantity"[:\s]*([0-9]+)'],
        "box_weight": [r'Box Weight[:\s]*([0-9.]+ lbs?)', r'"boxWeight"[:\s]*"([^"]+)"'],
        "edge_type": [r'Edge Type[:\s]*([^<\n,]+)', r'"edgeType"[:\s]*"([^"]+)"'],
        "shade_variation": [r'Shade Variation[:\s]*([VL][0-9])', r'"shadeVariation"[:\s]*"([^"]+)"'],
        "number_of_faces": [r'Number of Faces[:\s]*([0-9]+)', r'"numberOfFaces"[:\s]*([0-9]+)'],
        "directional_layout": [r'Directional Layout[:\s]*(Yes|No)', r'"directionalLayout"[:\s]*"([^"]+)"'],
        "country_of_origin": [r'Country of Origin[:\s]*([^<\n,]+)', r'"countryOfOrigin"[:\s]*"([^"]+)"'],
    }
    
    print("Recommended extraction patterns:")
    for field, patterns in extraction_patterns.items():
        print(f"\n   {field}:")
        for i, pattern in enumerate(patterns, 1):
            print(f"     Pattern {i}: {pattern}")
    
    return {
        "total_available": total_available,
        "total_captured": total_captured,
        "capture_rate": capture_rate,
        "missing_fields": missing_fields,
        "recommended_fields": recommended_fields,
        "extraction_patterns": extraction_patterns
    }

if __name__ == "__main__":
    audit_results = audit_tile_data_extraction()
    
    print(f"\n🎯 NEXT STEPS")
    print("-" * 40)
    print("1. Apply schema enhancements to database")
    print("2. Update extraction logic in curl_scraper.py")
    print("3. Add specification extraction patterns")
    print("4. Test with multiple tile SKUs for validation")
    print("5. Implement auto-expanding schema detection")