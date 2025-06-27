#!/usr/bin/env python3
"""
Sync Manager - Syncs data between n8n-postgres and Supabase
"""

import psycopg2
import psycopg2.extras
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseSyncManager:
    """Manages data synchronization between n8n-postgres and Supabase"""
    
    def __init__(self):
        # Source database (n8n-postgres) - accessed via docker exec
        self.source_container = 'n8n-postgres'
        self.source_db = 'postgres'
        
        # Target database (Supabase) - accessed via docker exec
        self.target_container = 'supabase-db'
        self.target_db = 'postgres'
        
        self.last_sync = None
        self.sync_stats = {
            'total_synced': 0,
            'last_sync_time': None,
            'last_error': None,
            'sync_count': 0
        }
    
    def get_source_connection(self):
        """Get connection to source database via docker exec"""
        # We'll use docker exec commands for source access
        return None
    
    def get_target_connection(self):
        """Get connection to target database via docker exec"""
        # We'll use docker exec commands for target access too
        return None
    
    def test_connections(self) -> Dict[str, Any]:
        """Test both source and target connections"""
        results = {}
        
        # Test source (n8n-postgres via docker)
        try:
            result = subprocess.run([
                'docker', 'exec', self.source_container, 
                'psql', '-U', 'postgres', '-d', self.source_db, 
                '-c', 'SELECT COUNT(*) FROM product_data;'
            ], capture_output=True, text=True, check=True)
            
            count = int(result.stdout.strip().split('\n')[-2].strip())
            results['source'] = {
                'connected': True,
                'product_count': count,
                'message': f'Found {count} products in source database'
            }
        except Exception as e:
            results['source'] = {
                'connected': False,
                'error': str(e),
                'message': f'Source connection failed: {str(e)}'
            }
        
        # Test target (Supabase via network)
        try:
            conn = self.get_target_connection()
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'product_data'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM product_data;")
                count = cursor.fetchone()[0]
            else:
                count = 0
            
            cursor.close()
            conn.close()
            
            results['target'] = {
                'connected': True,
                'table_exists': table_exists,
                'product_count': count,
                'message': f'Target ready, {count} products synced'
            }
        except Exception as e:
            results['target'] = {
                'connected': False,
                'error': str(e),
                'message': f'Target connection failed: {str(e)}'
            }
        
        return results
    
    def initialize_target_table(self) -> Dict[str, Any]:
        """Create product_data table in Supabase if it doesn't exist"""
        try:
            conn = self.get_target_connection()
            cursor = conn.cursor()
            
            # Create table with same structure as source
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_data (
                    id SERIAL PRIMARY KEY,
                    url VARCHAR(500) UNIQUE NOT NULL,
                    sku VARCHAR(50),
                    title TEXT,
                    price_per_box DECIMAL(10,2),
                    price_per_sqft DECIMAL(10,2),
                    coverage TEXT,
                    finish TEXT,
                    color TEXT,
                    size_shape TEXT,
                    description TEXT,
                    specifications JSONB,
                    resources TEXT,
                    raw_html TEXT,
                    raw_markdown TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    images TEXT,
                    collection_links TEXT,
                    brand VARCHAR(100),
                    primary_image TEXT,
                    image_variants JSONB
                );
            """)
            
            # Create useful indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_product_sku ON product_data(sku);
                CREATE INDEX IF NOT EXISTS idx_product_scraped_at ON product_data(scraped_at);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_product_url ON product_data(url);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Target table initialized successfully'
            }
            
        except Exception as e:
            logger.error(f"Error initializing target table: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_source_data(self) -> List[Dict[str, Any]]:
        """Get all product data from source database"""
        try:
            # Use docker exec to get data as CSV
            result = subprocess.run([
                'docker', 'exec', self.source_container,
                'psql', '-U', 'postgres', '-d', self.source_db,
                '-c', 'COPY (SELECT * FROM product_data ORDER BY id) TO STDOUT CSV HEADER;'
            ], capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                return []
            
            # Parse CSV data
            import csv
            import io
            
            csv_data = io.StringIO(result.stdout)
            reader = csv.DictReader(csv_data)
            products = []
            
            for row in reader:
                # Convert empty strings to None
                for key, value in row.items():
                    if value == '':
                        row[key] = None
                
                # Parse JSON fields
                for json_field in ['specifications', 'image_variants']:
                    if row.get(json_field):
                        try:
                            row[json_field] = json.loads(row[json_field])
                        except json.JSONDecodeError:
                            row[json_field] = None
                
                products.append(row)
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting source data: {e}")
            return []
    
    def sync_data(self, force_full_sync: bool = False) -> Dict[str, Any]:
        """Sync data from source to target"""
        try:
            sync_start = datetime.now()
            
            # Initialize target table
            init_result = self.initialize_target_table()
            if not init_result['success']:
                return init_result
            
            # Get source data
            source_products = self.get_source_data()
            if not source_products:
                return {
                    'success': False,
                    'error': 'No data found in source database'
                }
            
            # Connect to target
            conn = self.get_target_connection()
            cursor = conn.cursor()
            
            synced_count = 0
            updated_count = 0
            error_count = 0
            
            for product in source_products:
                try:
                    # Prepare data for insertion
                    columns = list(product.keys())
                    values = [product[col] for col in columns]
                    
                    # Convert JSON fields back to strings for insertion
                    for i, col in enumerate(columns):
                        if col in ['specifications', 'image_variants'] and values[i] is not None:
                            values[i] = json.dumps(values[i])
                    
                    # Build upsert query
                    placeholders = ', '.join(['%s'] * len(values))
                    columns_str = ', '.join(columns)
                    
                    # Exclude id from updates to avoid conflicts
                    update_columns = [col for col in columns if col != 'id']
                    update_assignments = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
                    
                    query = f"""
                        INSERT INTO product_data ({columns_str})
                        VALUES ({placeholders})
                        ON CONFLICT (url) DO UPDATE SET
                            {update_assignments},
                            updated_at = CURRENT_TIMESTAMP;
                    """
                    
                    cursor.execute(query, values)
                    
                    if cursor.rowcount > 0:
                        synced_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing product {product.get('sku', 'unknown')}: {e}")
                    error_count += 1
                    continue
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update sync stats
            sync_end = datetime.now()
            self.sync_stats.update({
                'total_synced': synced_count + updated_count,
                'last_sync_time': sync_end.isoformat(),
                'last_error': None,
                'sync_count': self.sync_stats['sync_count'] + 1,
                'duration_seconds': (sync_end - sync_start).total_seconds()
            })
            
            return {
                'success': True,
                'synced_count': synced_count,
                'updated_count': updated_count,
                'error_count': error_count,
                'total_products': len(source_products),
                'duration_seconds': self.sync_stats['duration_seconds'],
                'message': f'Synced {synced_count} new, updated {updated_count} existing products'
            }
            
        except Exception as e:
            logger.error(f"Error during sync: {e}")
            self.sync_stats['last_error'] = str(e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and statistics"""
        connections = self.test_connections()
        
        return {
            'connections': connections,
            'stats': self.sync_stats,
            'last_sync': self.sync_stats.get('last_sync_time'),
            'ready_to_sync': (
                connections.get('source', {}).get('connected', False) and
                connections.get('target', {}).get('connected', False)
            )
        }
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old data from target database"""
        try:
            conn = self.get_target_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM product_data 
                WHERE updated_at < NOW() - INTERVAL '%s days'
                RETURNING id;
            """, (days,))
            
            deleted_ids = cursor.fetchall()
            deleted_count = len(deleted_ids)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Cleaned up {deleted_count} old records'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_data_comparison(self) -> Dict[str, Any]:
        """Compare data between source and target"""
        try:
            connections = self.test_connections()
            
            source_count = connections.get('source', {}).get('product_count', 0)
            target_count = connections.get('target', {}).get('product_count', 0)
            
            sync_percentage = (target_count / source_count * 100) if source_count > 0 else 0
            
            return {
                'source_count': source_count,
                'target_count': target_count,
                'sync_percentage': round(sync_percentage, 1),
                'missing_count': max(0, source_count - target_count),
                'is_in_sync': source_count == target_count,
                'last_comparison': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing data: {e}")
            return {
                'error': str(e)
            }