#!/usr/bin/env python3
"""
Simple Tileshop RAG System - Direct database connection approach
"""

import psycopg2
import json
import logging
from typing import List, Dict, Any
import hashlib
import struct
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTileshopRAG:
    def __init__(self):
        # Database connection parameters
        self.n8n_db_params = {
            'host': '127.0.0.1',  # Use IPv4 explicitly
            'port': 5432,
            'database': 'postgres',
            'user': 'robertsher',  # Use system user for external connections
            'password': None  # No password needed for system user
        }
        
        # Connect to Supabase via container
        self.supabase_container = 'supabase-db'
    
    def get_supabase_connection(self):
        """Get connection to Supabase database via docker exec"""
        # Use docker exec like other components
        return None
        
    def get_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding"""
        hash_obj = hashlib.md5(text.encode())
        seed = struct.unpack('I', hash_obj.digest()[:4])[0]
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def sync_data(self):
        """Sync product data from n8n to Supabase"""
        try:
            # Get products from n8n
            conn = self.get_n8n_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, url, sku, title, description, specifications, 
                       price_per_box, price_per_sqft, finish, color, size_shape
                FROM product_data;
            """)
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            
            logger.info(f"Found {len(products)} products to sync")
            
            # Create vector table in Supabase
            import subprocess
            
            # First create the table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS product_embeddings (
                id SERIAL PRIMARY KEY,
                product_id INTEGER UNIQUE,
                url TEXT,
                sku TEXT,
                title TEXT,
                content TEXT,
                embedding vector(384),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            subprocess.run([
                'docker', 'exec', 'supabase-db', 'psql', 
                '-U', 'postgres', '-d', 'postgres', 
                '-c', create_table_sql
            ], check=True)
            
            # Process and insert each product
            for product in products:
                product_id, url, sku, title, description, specifications, price_per_box, price_per_sqft, finish, color, size_shape = product
                
                # Create content for embedding
                content_parts = [
                    f"Title: {title or ''}",
                    f"SKU: {sku or ''}",
                    f"Description: {description or ''}",
                    f"Finish: {finish or ''}",
                    f"Color: {color or ''}",
                    f"Size: {size_shape or ''}",
                    f"Price per box: ${price_per_box or 0}",
                    f"Price per sq ft: ${price_per_sqft or 0}"
                ]
                
                content = "\\n".join(content_parts)
                
                # Create metadata
                metadata = {
                    'price_per_box': float(price_per_box) if price_per_box else None,
                    'price_per_sqft': float(price_per_sqft) if price_per_sqft else None,
                    'finish': finish,
                    'color': color,
                    'size_shape': size_shape
                }
                
                # Generate smaller embedding (384 dimensions)
                embedding = self.get_mock_embedding(content)[:384]
                embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                
                # Escape content and metadata for SQL
                content = content.replace("'", "''")
                metadata_str = json.dumps(metadata).replace("'", "''")
                title = (title or '').replace("'", "''")
                url = (url or '').replace("'", "''")
                sku = (sku or '').replace("'", "''")
                
                insert_sql = f"""
                INSERT INTO product_embeddings 
                (product_id, url, sku, title, content, embedding, metadata)
                VALUES ({product_id}, '{url}', '{sku}', '{title}', '{content}', '{embedding_str}', '{metadata_str}')
                ON CONFLICT (product_id) DO UPDATE SET
                    url = EXCLUDED.url,
                    sku = EXCLUDED.sku,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata;
                """
                
                result = subprocess.run([
                    'docker', 'exec', 'supabase-db', 'psql', 
                    '-U', 'postgres', '-d', 'postgres', 
                    '-c', insert_sql
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Error inserting product {sku}: {result.stderr}")
                else:
                    logger.info(f"Synced product {sku}: {title}")
            
            logger.info("Sync completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing data: {e}")
            return False
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search products using docker exec from Supabase"""
        try:
            # Use docker exec to search Supabase instead
            import subprocess
            import csv
            import io
            
            # Escape the query for SQL
            query_escaped = query.replace("'", "''")
            
            # Use PostgreSQL full-text search for now
            cursor.execute("""
                SELECT url, sku, title, description, price_per_box, price_per_sqft,
                       finish, color, size_shape, specifications,
                       ts_rank(to_tsvector('english', 
                           COALESCE(title, '') || ' ' || 
                           COALESCE(description, '') || ' ' || 
                           COALESCE(finish, '') || ' ' || 
                           COALESCE(color, '') || ' ' || 
                           COALESCE(size_shape, '')
                       ), plainto_tsquery('english', %s)) as relevance
                FROM product_data
                WHERE to_tsvector('english', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(description, '') || ' ' || 
                    COALESCE(finish, '') || ' ' || 
                    COALESCE(color, '') || ' ' || 
                    COALESCE(size_shape, '')
                ) @@ plainto_tsquery('english', %s)
                ORDER BY relevance DESC
                LIMIT %s;
            """, (query, query, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            formatted_results = []
            for result in results:
                url, sku, title, description, price_per_box, price_per_sqft, finish, color, size_shape, specifications, relevance = result
                formatted_results.append({
                    'url': url,
                    'sku': sku,
                    'title': title,
                    'description': description,
                    'price_per_box': price_per_box,
                    'price_per_sqft': price_per_sqft,
                    'finish': finish,
                    'color': color,
                    'size_shape': size_shape,
                    'specifications': specifications,
                    'relevance': float(relevance)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def chat(self, query: str) -> str:
        """Generate chat response"""
        results = self.search_products(query)
        
        if not results:
            return "I couldn't find any products matching your query. Try searching for tile types, colors, finishes, or sizes."
        
        response_parts = [f"Here are {len(results)} products that match your query:\n"]
        
        for i, result in enumerate(results, 1):
            price_info = ""
            if result['price_per_box']:
                price_info = f" - ${result['price_per_box']:.2f}/box"
            if result['price_per_sqft']:
                price_info += f" (${result['price_per_sqft']:.2f}/sq ft)"
            
            finish_color = []
            if result['finish']:
                finish_color.append(result['finish'])
            if result['color']:
                finish_color.append(result['color'])
            
            finish_color_str = " - " + " ".join(finish_color) if finish_color else ""
            size_str = f" - {result['size_shape']}" if result['size_shape'] else ""
            
            response_parts.append(
                f"{i}. **{result['title']}** (SKU: {result['sku']})\n"
                f"   {price_info}{finish_color_str}{size_str}\n"
                f"   {result['url']}\n"
            )
        
        return "\n".join(response_parts)