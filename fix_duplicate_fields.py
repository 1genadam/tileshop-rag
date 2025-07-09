#!/usr/bin/env python3
"""
Fix duplicate fields in existing product data
Remove camelCase duplicates and keep snake_case versions
"""

import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.db_manager import DatabaseManager

def clean_product_specifications():
    """Clean duplicate fields from product specifications"""
    
    # Database connection
    db_manager = DatabaseManager()
    conn = db_manager.get_connection()
    
    cursor = conn.cursor()
    
    # Get all products with specifications
    cursor.execute("SELECT id, sku, specifications FROM product_data WHERE specifications IS NOT NULL AND specifications != '{}'")
    products = cursor.fetchall()
    
    print(f"Found {len(products)} products with specifications")
    
    duplicates_to_remove = [
        'approximatesize',  # Keep dimensions or approximate_size
        'boxweight',        # Keep box_weight
        'directionallayout', # Keep directional_layout
        'surfaceabrasions', # Keep pei_rating or surface_abrasion
        'shadevariation',   # Keep shade_variation
        'countryoforigin',  # Keep country_of_origin
    ]
    
    renames = {
        'surfaceabrasions': 'surface_abrasion',
        'shadevariation': 'shade_variation', 
        'countryoforigin': 'country_of_origin',
        'frostresistance': 'frost_resistance'
    }
    
    updated_count = 0
    
    for product_id, sku, specs_json in products:
        try:
            specs = json.loads(specs_json)
            modified = False
            
            # Remove duplicates
            for duplicate in duplicates_to_remove:
                if duplicate in specs:
                    print(f"Removing {duplicate} from SKU {sku}")
                    del specs[duplicate]
                    modified = True
            
            # Rename camelCase fields to proper names
            for old_name, new_name in renames.items():
                if old_name in specs and new_name not in specs:
                    print(f"Renaming {old_name} -> {new_name} for SKU {sku}")
                    specs[new_name] = specs[old_name]
                    del specs[old_name]
                    modified = True
                elif old_name in specs and new_name in specs:
                    # Both exist, remove the camelCase one
                    print(f"Removing duplicate {old_name} (keeping {new_name}) for SKU {sku}")
                    del specs[old_name]
                    modified = True
            
            if modified:
                # Update the database
                updated_specs = json.dumps(specs)
                cursor.execute(
                    "UPDATE product_data SET specifications = %s, updated_at = %s WHERE id = %s",
                    (updated_specs, datetime.now(), product_id)
                )
                updated_count += 1
                print(f"✅ Updated SKU {sku}")
        
        except Exception as e:
            print(f"❌ Error processing SKU {sku}: {e}")
    
    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n🎉 Successfully updated {updated_count} products")
    print("Duplicate fields removed and camelCase fields renamed")

if __name__ == "__main__":
    print("🔧 Fixing duplicate fields in existing product data...")
    print("=" * 60)
    clean_product_specifications()