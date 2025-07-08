#!/usr/bin/env python3
"""
Enhanced Data Processing Script
Applies LLM-based categorization and material detection to existing product data
Updates products with improved accuracy and field completeness
"""

import psycopg2
import json
import os
import sys
from typing import Dict, List, Any, Optional
from enhanced_categorization_system import EnhancedCategorizer
from enhanced_specification_extractor import EnhancedSpecificationExtractor
import time

# Load API key from environment
required_env_key = 'ANTHROPIC_API_KEY'
if required_env_key not in os.environ:
    raise ValueError(f"{required_env_key} environment variable must be set")

class DataEnhancer:
    def __init__(self):
        self.categorizer = EnhancedCategorizer()
        self.spec_extractor = EnhancedSpecificationExtractor()
        self.processed_count = 0
        self.updated_count = 0
        self.error_count = 0
        
    def connect_db(self):
        """Connect to the PostgreSQL database"""
        try:
            return psycopg2.connect(
                host='localhost',
                port=5432,
                database='postgres',
                user='postgres',
                password='postgres'
            )
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def get_products_needing_enhancement(self, limit: int = None) -> List[Dict]:
        """Get products that need LLM-based enhancement"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Get products with poor categorization or missing enhanced data
            query = """
            SELECT id, title, description, brand, material_type, product_category, 
                   subcategory, price_per_box, price_per_piece, price_per_sqft,
                   specifications, sku, url
            FROM product_data 
            WHERE 
                (product_category = 'tiles' AND title ILIKE '%diamond%tool%') OR
                (product_category = 'tiles' AND title ILIKE '%polish%') OR
                (product_category = 'tiles' AND title ILIKE '%bit%') OR
                (product_category = 'tiles' AND title ILIKE '%grout%') OR
                (material_type IS NULL OR material_type = '') OR
                (product_category IS NULL OR product_category = '') OR
                (specifications IS NULL OR specifications = '{}')
            """
            
            if limit:
                query += f" LIMIT {limit}"
                
            cursor.execute(query)
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                product = {
                    'id': row[0],
                    'title': row[1] or '',
                    'description': row[2] or '',
                    'brand': row[3] or '',
                    'material_type': row[4],
                    'product_category': row[5],
                    'subcategory': row[6],
                    'price_per_box': row[7],
                    'price_per_piece': row[8],
                    'price_per_sqft': row[9],
                    'specifications': row[10] or '{}',
                    'sku': row[11] or '',
                    'url': row[12] or ''
                }
                products.append(product)
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"❌ Failed to query products: {e}")
            conn.close()
            return []
    
    def enhance_product(self, product: Dict) -> Dict:
        """Apply enhanced LLM-based processing to a single product"""
        enhanced_product = product.copy()
        updates_made = []
        
        try:
            # 1. Enhanced Material Detection
            if not product.get('material_type') or product['material_type'] in ['', 'unknown']:
                material = self.categorizer.extract_material_type(product)
                if material and material != product.get('material_type'):
                    enhanced_product['material_type'] = material
                    updates_made.append(f"Material: {product.get('material_type')} → {material}")
            
            # 2. Enhanced Category Detection
            category_result = self.categorizer.categorize_product(product)
            if category_result:
                old_category = f"{product.get('product_category', '')}/{product.get('subcategory', '')}"
                new_category = f"{category_result.primary_category}/{category_result.subcategory}"
                
                if new_category != old_category:
                    enhanced_product['product_category'] = category_result.primary_category
                    enhanced_product['subcategory'] = category_result.subcategory
                    enhanced_product['product_type'] = category_result.product_type
                    enhanced_product['application_areas'] = json.dumps(category_result.application_areas)
                    enhanced_product['installation_complexity'] = category_result.installation_complexity
                    updates_made.append(f"Category: {old_category} → {new_category}")
            
            # 3. LLM Category Validation
            try:
                llm_category = self.spec_extractor._detect_category_with_llm(
                    product.get('title', ''), 
                    f"<html>{product.get('description', '')}</html>"
                )
                if llm_category and llm_category != enhanced_product.get('product_category'):
                    # Store LLM suggestion for comparison
                    enhanced_product['llm_suggested_category'] = llm_category
                    updates_made.append(f"LLM suggests: {llm_category}")
            except Exception as e:
                print(f"  ⚠️ LLM category detection failed: {e}")
            
            # 4. Enhanced Specifications
            try:
                current_specs = json.loads(product.get('specifications', '{}'))
                if len(current_specs) < 5:  # Enhance if few specifications
                    # This would require the full HTML content, skip for now
                    pass
            except:
                pass
            
            enhanced_product['enhancement_applied'] = True
            enhanced_product['enhancement_timestamp'] = time.time()
            enhanced_product['updates_made'] = json.dumps(updates_made)
            
            return enhanced_product
            
        except Exception as e:
            print(f"  ❌ Enhancement failed: {e}")
            return product
    
    def update_product_in_db(self, product: Dict) -> bool:
        """Update enhanced product in database"""
        conn = self.connect_db()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Update product with enhanced data (only existing columns)
            update_query = """
            UPDATE product_data SET 
                material_type = %s,
                product_category = %s,
                subcategory = %s,
                product_type = %s,
                application_areas = %s,
                installation_complexity = %s
            WHERE id = %s
            """
            
            cursor.execute(update_query, (
                product.get('material_type'),
                product.get('product_category'),
                product.get('subcategory'),
                product.get('product_type'),
                product.get('application_areas'),
                product.get('installation_complexity'),
                product['id']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"  ❌ Database update failed: {e}")
            conn.close()
            return False
    
    def enhance_all_products(self, batch_size: int = 100, max_products: int = None):
        """Enhance all products needing LLM processing"""
        print("🎯 ENHANCED DATA PROCESSING - LLM Categorization & Material Detection")
        print("=" * 80)
        
        # Get products needing enhancement
        products = self.get_products_needing_enhancement(max_products)
        total_products = len(products)
        
        if total_products == 0:
            print("✅ No products found needing enhancement")
            return
        
        print(f"📊 Found {total_products} products needing enhancement")
        print(f"🔄 Processing in batches of {batch_size}")
        print()
        
        for i, product in enumerate(products):
            print(f"Processing {i+1}/{total_products}: {product['title'][:50]}...")
            
            try:
                # Enhance the product
                enhanced_product = self.enhance_product(product)
                
                # Update in database
                if self.update_product_in_db(enhanced_product):
                    self.updated_count += 1
                    updates = json.loads(enhanced_product.get('updates_made', '[]'))
                    if updates:
                        print(f"  ✅ Enhanced: {', '.join(updates)}")
                    else:
                        print(f"  ✓ Validated (no changes needed)")
                else:
                    self.error_count += 1
                    print(f"  ❌ Database update failed")
                
                self.processed_count += 1
                
                # Rate limiting for API calls
                time.sleep(0.5)  # Small delay between products
                
                # Progress report every 10 products
                if (i + 1) % 10 == 0:
                    print()
                    print(f"📊 Progress: {i+1}/{total_products} ({((i+1)/total_products)*100:.1f}%)")
                    print(f"   Updated: {self.updated_count}, Errors: {self.error_count}")
                    print()
                
            except Exception as e:
                self.error_count += 1
                print(f"  ❌ Processing failed: {e}")
        
        # Final summary
        print()
        print("🏆 ENHANCEMENT COMPLETE")
        print("=" * 50)
        print(f"Total Processed: {self.processed_count}")
        print(f"Successfully Updated: {self.updated_count}")
        print(f"Errors: {self.error_count}")
        print(f"Success Rate: {(self.updated_count/self.processed_count)*100:.1f}%")
    
    def analyze_current_data_quality(self):
        """Analyze current data quality and categorization issues"""
        conn = self.connect_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            print("📊 CURRENT DATA QUALITY ANALYSIS")
            print("=" * 50)
            
            # Total products
            cursor.execute("SELECT COUNT(*) FROM product_data")
            total = cursor.fetchone()[0]
            print(f"Total Products: {total:,}")
            
            # Material type distribution
            print("\n🧱 Material Type Distribution:")
            cursor.execute("""
                SELECT material_type, COUNT(*) as count 
                FROM product_data 
                GROUP BY material_type 
                ORDER BY count DESC 
                LIMIT 10
            """)
            for material, count in cursor.fetchall():
                print(f"  {material or 'NULL'}: {count:,}")
            
            # Category distribution
            print("\n📂 Category Distribution:")
            cursor.execute("""
                SELECT product_category, COUNT(*) as count 
                FROM product_data 
                GROUP BY product_category 
                ORDER BY count DESC 
                LIMIT 10
            """)
            for category, count in cursor.fetchall():
                print(f"  {category or 'NULL'}: {count:,}")
            
            # Potential misclassifications
            print("\n⚠️ Potential Misclassifications:")
            cursor.execute("""
                SELECT COUNT(*) FROM product_data 
                WHERE product_category = 'tiles' AND (
                    title ILIKE '%diamond%tool%' OR 
                    title ILIKE '%polish%' OR 
                    title ILIKE '%bit%' OR
                    title ILIKE '%grout%'
                )
            """)
            misclassified = cursor.fetchone()[0]
            print(f"  Tools classified as tiles: {misclassified}")
            
            # Missing data
            print("\n❌ Missing Data:")
            cursor.execute("SELECT COUNT(*) FROM product_data WHERE material_type IS NULL OR material_type = ''")
            missing_material = cursor.fetchone()[0]
            print(f"  Missing material type: {missing_material}")
            
            cursor.execute("SELECT COUNT(*) FROM product_data WHERE product_category IS NULL OR product_category = ''")
            missing_category = cursor.fetchone()[0]
            print(f"  Missing category: {missing_category}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            conn.close()

def main():
    enhancer = DataEnhancer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        enhancer.analyze_current_data_quality()
    else:
        # First analyze current data
        enhancer.analyze_current_data_quality()
        print()
        
        # Then enhance the data
        max_products = 500  # Start with 500 products for safety
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            max_products = int(sys.argv[1])
        
        enhancer.enhance_all_products(max_products=max_products)

if __name__ == "__main__":
    main()