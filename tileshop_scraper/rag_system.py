#!/usr/bin/env python3
"""
Tileshop RAG System - Retrieval-Augmented Generation for Product Data
Uses Supabase vector database for semantic search over tileshop product data
"""

import os
import json
import logging
import psycopg2
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TileshopRAG:
    def __init__(self):
        # Supabase configuration
        self.supabase_url = "http://localhost:8000"
        self.supabase_key = "8bwkof8kQ23Qyk5Rgf9gXUzbqRoBmFbEBhffWHk0VzE="  # anon key from .env
        self.service_role_key = "6hzgXqrgIPUGm2QrZir/3xzWRLZ3VAQ0FZ64upOg3Io="  # service role key
        
        # Database configurations
        self.n8n_db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Postgres1'
        }
        
        self.supabase_db_config = {
            'host': 'localhost',
            'port': 5433,  # Supabase mapped port
            'database': 'postgres',  # Use postgres database initially
            'user': 'postgres',
            'password': 'supabase123'
        }
        
        self.initialize_vector_tables()
    
    def initialize_vector_tables(self):
        """Initialize vector storage tables in Supabase"""
        try:
            conn = psycopg2.connect(**self.supabase_db_config)
            cursor = conn.cursor()
            
            # Enable vector extension
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create vector table for product embeddings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_embeddings (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER UNIQUE,
                    url TEXT,
                    sku TEXT,
                    title TEXT,
                    content TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for vector similarity search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS product_embeddings_embedding_idx 
                ON product_embeddings USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Vector tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector tables: {e}")
    
    def get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API (placeholder - would need actual API key)"""
        # For now, return a mock embedding vector
        # In production, you would use:
        # import openai
        # response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        # return response['data'][0]['embedding']
        
        # Mock embedding (1536 dimensions for text-embedding-ada-002)
        import hashlib
        import struct
        
        # Create deterministic but varied embedding based on text
        hash_obj = hashlib.md5(text.encode())
        seed = struct.unpack('I', hash_obj.digest()[:4])[0]
        
        import random
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def sync_product_data(self):
        """Sync product data from n8n-postgres to Supabase with embeddings"""
        try:
            # Get product data from n8n database
            n8n_conn = psycopg2.connect(**self.n8n_db_config)
            n8n_cursor = n8n_conn.cursor()
            
            n8n_cursor.execute("""
                SELECT id, url, sku, title, description, specifications, 
                       price_per_box, price_per_sqft, finish, color, size_shape
                FROM product_data 
                ORDER BY id;
            """)
            
            products = n8n_cursor.fetchall()
            n8n_cursor.close()
            n8n_conn.close()
            
            logger.info(f"Found {len(products)} products to sync")
            
            # Connect to Supabase
            supabase_conn = psycopg2.connect(**self.supabase_db_config)
            supabase_cursor = supabase_conn.cursor()
            
            for product in products:
                product_id, url, sku, title, description, specifications, price_per_box, price_per_sqft, finish, color, size_shape = product
                
                # Create searchable content
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
                
                if specifications:
                    if isinstance(specifications, str):
                        specs_dict = json.loads(specifications)
                    else:
                        specs_dict = specifications
                    
                    for key, value in specs_dict.items():
                        if value:
                            content_parts.append(f"{key}: {value}")
                
                content = "\n".join(content_parts)
                
                # Generate embedding
                embedding = self.get_openai_embedding(content)
                
                # Prepare metadata
                metadata = {
                    'price_per_box': float(price_per_box) if price_per_box else None,
                    'price_per_sqft': float(price_per_sqft) if price_per_sqft else None,
                    'finish': finish,
                    'color': color,
                    'size_shape': size_shape,
                    'specifications': specifications
                }
                
                # Insert or update embedding
                supabase_cursor.execute("""
                    INSERT INTO product_embeddings 
                    (product_id, url, sku, title, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO UPDATE SET
                        url = EXCLUDED.url,
                        sku = EXCLUDED.sku,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata;
                """, (product_id, url, sku, title, content, embedding, json.dumps(metadata)))
                
                logger.info(f"Synced product {sku}: {title}")
            
            supabase_conn.commit()
            supabase_cursor.close()
            supabase_conn.close()
            
            logger.info(f"Successfully synced {len(products)} products with embeddings")
            
        except Exception as e:
            logger.error(f"Error syncing product data: {e}")
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for products using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.get_openai_embedding(query)
            
            # Search in Supabase
            conn = psycopg2.connect(**self.supabase_db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT product_id, url, sku, title, content, metadata,
                       1 - (embedding <=> %s::vector) as similarity
                FROM product_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, query_embedding, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Format results
            formatted_results = []
            for result in results:
                product_id, url, sku, title, content, metadata, similarity = result
                formatted_results.append({
                    'product_id': product_id,
                    'url': url,
                    'sku': sku,
                    'title': title,
                    'content': content,
                    'metadata': metadata,
                    'similarity': float(similarity)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate a response based on search results"""
        if not search_results:
            return "I couldn't find any relevant products for your query. Please try rephrasing your question."
        
        # Simple template-based response generation
        response_parts = [f"Based on your query '{query}', here are the most relevant products:\n"]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            price_info = ""
            if metadata.get('price_per_box'):
                price_info = f" - ${metadata['price_per_box']:.2f}/box"
            if metadata.get('price_per_sqft'):
                price_info += f" (${metadata['price_per_sqft']:.2f}/sq ft)"
            
            response_parts.append(
                f"{i}. **{result['title']}** (SKU: {result['sku']})\n"
                f"   {price_info}\n"
                f"   Similarity: {result['similarity']:.3f}\n"
                f"   URL: {result['url']}\n"
            )
        
        return "\n".join(response_parts)
    
    def chat(self, query: str) -> str:
        """Main chat interface"""
        logger.info(f"User query: {query}")
        
        # Search for relevant products
        search_results = self.search_products(query)
        
        # Generate response
        response = self.generate_response(query, search_results)
        
        logger.info(f"Generated response with {len(search_results)} results")
        return response

def main():
    """Interactive chat interface"""
    rag = TileshopRAG()
    
    print("🏠 Tileshop RAG System")
    print("Ask me about tiles, products, specifications, or anything related to Tileshop!")
    print("Type 'sync' to sync product data, 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'sync':
                print("Syncing product data...")
                rag.sync_product_data()
                print("Sync complete!")
                continue
            elif not user_input:
                continue
            
            response = rag.chat(user_input)
            print(f"\nBot: {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()