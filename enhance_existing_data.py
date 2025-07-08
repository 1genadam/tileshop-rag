#!/usr/bin/env python3
"""
Enhanced Data Processing Script for Tileshop RAG Production
Applies LLM-based processing to existing product data for improved categorization
"""

import os
import json
import logging
import psycopg2
from typing import Dict, List, Any, Optional
import anthropic
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TileshopDataEnhancer:
    """Enhanced data processing system with LLM integration"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'robertsher'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }
        
        # Initialize Claude API client
        self.claude_client = None
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            try:
                self.claude_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Claude API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude API client: {e}")
                raise
        else:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        # Enhanced material detection patterns
        self.material_patterns = {
            'ceramic': ['ceramic', 'glazed ceramic', 'unglazed ceramic'],
            'porcelain': ['porcelain', 'rectified porcelain', 'through-body porcelain'],
            'natural_stone': ['marble', 'granite', 'travertine', 'limestone', 'slate', 'quartzite'],
            'glass': ['glass', 'recycled glass', 'frosted glass', 'iridescent glass'],
            'metal': ['stainless steel', 'aluminum', 'copper', 'brass'],
            'wood': ['wood', 'bamboo', 'cork'],
            'vinyl': ['vinyl', 'lvt', 'luxury vinyl tile'],
            'concrete': ['concrete', 'cement']
        }
        
        # Enhanced type detection patterns
        self.type_patterns = {
            'floor_tile': ['floor tile', 'flooring', 'floor'],
            'wall_tile': ['wall tile', 'wall', 'backsplash'],
            'mosaic': ['mosaic', 'penny round', 'hexagon', 'subway'],
            'large_format': ['large format', '24x24', '24x48', '32x32'],
            'plank': ['plank', 'wood plank', 'wood look'],
            'accent': ['accent', 'decorative', 'feature'],
            'trim': ['trim', 'bullnose', 'chair rail', 'base'],
            'outdoor': ['outdoor', 'exterior', 'patio', 'pool']
        }
    
    def connect_to_database(self) -> psycopg2.connection:
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("Database connection established")
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_products_for_enhancement(self, conn: psycopg2.connection, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products that need LLM enhancement"""
        try:
            cursor = conn.cursor()
            
            # Get products with basic information for LLM processing
            query = """
                SELECT sku, title, description, brand, category, 
                       product_type, material, size_info, color, finish,
                       price, specifications, features
                FROM products 
                WHERE sku IS NOT NULL 
                ORDER BY sku
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            columns = [desc[0] for desc in cursor.description]
            products = []
            
            for row in cursor.fetchall():
                product = dict(zip(columns, row))
                products.append(product)
            
            cursor.close()
            logger.info(f"Retrieved {len(products)} products for enhancement")
            return products
            
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            raise
    
    def enhance_product_with_llm(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance single product using Claude API"""
        try:
            # Create enhancement prompt
            prompt = f"""
            Analyze this tile/flooring product and provide enhanced categorization:
            
            Product Details:
            - SKU: {product.get('sku', 'N/A')}
            - Title: {product.get('title', 'N/A')}
            - Description: {product.get('description', 'N/A')}
            - Brand: {product.get('brand', 'N/A')}
            - Current Category: {product.get('category', 'N/A')}
            - Current Material: {product.get('material', 'N/A')}
            - Current Type: {product.get('product_type', 'N/A')}
            - Size: {product.get('size_info', 'N/A')}
            - Color: {product.get('color', 'N/A')}
            - Finish: {product.get('finish', 'N/A')}
            - Features: {product.get('features', 'N/A')}
            - Specifications: {product.get('specifications', 'N/A')}
            
            Please provide enhanced categorization in this exact JSON format:
            {{
                "enhanced_material": "primary material (ceramic, porcelain, natural_stone, glass, metal, wood, vinyl, concrete)",
                "enhanced_type": "product type (floor_tile, wall_tile, mosaic, large_format, plank, accent, trim, outdoor)",
                "enhanced_category": "main category (tiles, installation_materials, tools, accessories)",
                "application_areas": ["bathroom", "kitchen", "living_room", "outdoor", "commercial"],
                "installation_complexity": "basic, intermediate, or advanced",
                "recommended_uses": ["floors", "walls", "backsplash", "accent", "outdoor"],
                "compatibility": ["wet_areas", "high_traffic", "outdoor_use", "heated_floors"],
                "size_category": "small, medium, large, extra_large",
                "finish_type": "matte, glossy, textured, natural, polished",
                "maintenance_level": "low, medium, high"
            }}
            
            Base your analysis on the product information provided. Be specific and accurate.
            """
            
            # Call Claude API
            response = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                
                try:
                    enhanced_data = json.loads(json_str)
                    logger.info(f"Successfully enhanced product {product.get('sku', 'N/A')}")
                    return enhanced_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error for {product.get('sku', 'N/A')}: {e}")
                    return None
            else:
                logger.error(f"No JSON found in response for {product.get('sku', 'N/A')}")
                return None
                
        except Exception as e:
            logger.error(f"LLM enhancement failed for {product.get('sku', 'N/A')}: {e}")
            return None
    
    def update_product_enhancements(self, conn: psycopg2.connection, sku: str, enhancements: Dict[str, Any]) -> bool:
        """Update product with enhanced data"""
        try:
            cursor = conn.cursor()
            
            # Update query with enhanced fields
            update_query = """
                UPDATE products SET 
                    enhanced_material = %s,
                    enhanced_type = %s,
                    enhanced_category = %s,
                    application_areas = %s,
                    installation_complexity = %s,
                    recommended_uses = %s,
                    compatibility = %s,
                    size_category = %s,
                    finish_type = %s,
                    maintenance_level = %s,
                    llm_enhanced = TRUE,
                    enhanced_timestamp = NOW()
                WHERE sku = %s
            """
            
            cursor.execute(update_query, (
                enhancements.get('enhanced_material'),
                enhancements.get('enhanced_type'),
                enhancements.get('enhanced_category'),
                json.dumps(enhancements.get('application_areas', [])),
                enhancements.get('installation_complexity'),
                json.dumps(enhancements.get('recommended_uses', [])),
                json.dumps(enhancements.get('compatibility', [])),
                enhancements.get('size_category'),
                enhancements.get('finish_type'),
                enhancements.get('maintenance_level'),
                sku
            ))
            
            conn.commit()
            cursor.close()
            logger.info(f"Updated enhancements for SKU {sku}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update enhancements for SKU {sku}: {e}")
            conn.rollback()
            return False
    
    def add_enhancement_columns(self, conn: psycopg2.connection):
        """Add enhancement columns to products table if they don't exist"""
        try:
            cursor = conn.cursor()
            
            # Check if columns exist and add if needed
            enhancement_columns = [
                "enhanced_material VARCHAR(100)",
                "enhanced_type VARCHAR(100)",
                "enhanced_category VARCHAR(100)",
                "application_areas TEXT",
                "installation_complexity VARCHAR(20)",
                "recommended_uses TEXT",
                "compatibility TEXT",
                "size_category VARCHAR(20)",
                "finish_type VARCHAR(50)",
                "maintenance_level VARCHAR(20)",
                "llm_enhanced BOOLEAN DEFAULT FALSE",
                "enhanced_timestamp TIMESTAMP"
            ]
            
            for column_def in enhancement_columns:
                column_name = column_def.split()[0]
                try:
                    cursor.execute(f"ALTER TABLE products ADD COLUMN {column_def}")
                    conn.commit()
                    logger.info(f"Added column: {column_name}")
                except psycopg2.Error as e:
                    if "already exists" in str(e):
                        logger.info(f"Column {column_name} already exists")
                        conn.rollback()
                    else:
                        logger.error(f"Error adding column {column_name}: {e}")
                        conn.rollback()
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error adding enhancement columns: {e}")
    
    def process_batch_enhancement(self, batch_size: int = 50, total_limit: int = 1000):
        """Process products in batches with LLM enhancement"""
        conn = self.connect_to_database()
        
        try:
            # Add enhancement columns if needed
            self.add_enhancement_columns(conn)
            
            total_processed = 0
            total_successful = 0
            total_errors = 0
            
            logger.info(f"Starting batch enhancement processing (batch_size={batch_size}, total_limit={total_limit})")
            
            while total_processed < total_limit:
                # Get next batch
                remaining = min(batch_size, total_limit - total_processed)
                products = self.get_products_for_enhancement(conn, remaining)
                
                if not products:
                    logger.info("No more products to process")
                    break
                
                # Process batch
                for product in products:
                    try:
                        # Enhance with LLM
                        enhancements = self.enhance_product_with_llm(product)
                        
                        if enhancements:
                            # Update database
                            if self.update_product_enhancements(conn, product['sku'], enhancements):
                                total_successful += 1
                            else:
                                total_errors += 1
                        else:
                            total_errors += 1
                        
                        total_processed += 1
                        
                        # Progress reporting
                        if total_processed % 10 == 0:
                            logger.info(f"Processed: {total_processed}/{total_limit}, "
                                      f"Successful: {total_successful}, Errors: {total_errors}")
                        
                        # Rate limiting
                        time.sleep(0.1)  # Small delay between API calls
                        
                    except Exception as e:
                        logger.error(f"Error processing product {product.get('sku', 'N/A')}: {e}")
                        total_errors += 1
                        total_processed += 1
                
                # Brief pause between batches
                time.sleep(1)
            
            # Final summary
            logger.info(f"\nBatch Enhancement Complete!")
            logger.info(f"Total Processed: {total_processed}")
            logger.info(f"Successful: {total_successful}")
            logger.info(f"Errors: {total_errors}")
            logger.info(f"Success Rate: {(total_successful/total_processed)*100:.1f}%")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
        finally:
            conn.close()
    
    def generate_enhancement_report(self):
        """Generate report on enhancement progress"""
        conn = self.connect_to_database()
        
        try:
            cursor = conn.cursor()
            
            # Get enhancement statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_products,
                    COUNT(*) FILTER (WHERE llm_enhanced = TRUE) as enhanced_products,
                    COUNT(DISTINCT enhanced_material) as unique_materials,
                    COUNT(DISTINCT enhanced_type) as unique_types,
                    COUNT(DISTINCT enhanced_category) as unique_categories,
                    COUNT(DISTINCT installation_complexity) as complexity_levels
                FROM products
            """
            
            cursor.execute(stats_query)
            stats = cursor.fetchone()
            
            # Material distribution
            material_query = """
                SELECT enhanced_material, COUNT(*) as count
                FROM products 
                WHERE enhanced_material IS NOT NULL
                GROUP BY enhanced_material
                ORDER BY count DESC
            """
            
            cursor.execute(material_query)
            materials = cursor.fetchall()
            
            # Type distribution
            type_query = """
                SELECT enhanced_type, COUNT(*) as count
                FROM products 
                WHERE enhanced_type IS NOT NULL
                GROUP BY enhanced_type
                ORDER BY count DESC
            """
            
            cursor.execute(type_query)
            types = cursor.fetchall()
            
            # Generate report
            report = f"""
# LLM Enhancement Report

## Summary Statistics
- **Total Products:** {stats[0]:,}
- **Enhanced Products:** {stats[1]:,}
- **Enhancement Rate:** {(stats[1]/stats[0]*100):.1f}%
- **Unique Materials:** {stats[2]}
- **Unique Types:** {stats[3]}
- **Unique Categories:** {stats[4]}
- **Complexity Levels:** {stats[5]}

## Material Distribution
"""
            
            for material, count in materials:
                report += f"- **{material}:** {count:,} products\n"
            
            report += "\n## Type Distribution\n"
            
            for type_name, count in types:
                report += f"- **{type_name}:** {count:,} products\n"
            
            cursor.close()
            
            # Save report
            with open('LLM_ENHANCEMENT_REPORT.md', 'w') as f:
                f.write(report)
            
            logger.info("Enhancement report generated: LLM_ENHANCEMENT_REPORT.md")
            print(report)
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
        finally:
            conn.close()

def main():
    """Main execution function"""
    enhancer = TileshopDataEnhancer()
    
    # Process products in batches
    enhancer.process_batch_enhancement(batch_size=25, total_limit=100)
    
    # Generate report
    enhancer.generate_enhancement_report()

if __name__ == "__main__":
    main()