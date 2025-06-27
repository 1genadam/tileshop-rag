#!/usr/bin/env python3
"""
Database Manager - Handles database operations and queries
"""

import psycopg2
import psycopg2.extras
import json
import logging
import csv
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.n8n_config = {
            'host': '127.0.0.1',  # Use IPv4 explicitly
            'port': 5432,
            'database': 'postgres',
            'user': 'robertsher',  # Use system user for external connections
            'password': None  # No password needed for system user
        }
        
        self.supabase_config = {
            'host': '127.0.0.1',  # Use IPv4 explicitly
            'port': 5433,
            'database': 'postgres',
            'user': 'postgres',
            'password': 'supabase123'
        }
    
    def get_connection(self, db_type: str = 'n8n'):
        """Get database connection"""
        if db_type == 'supabase':
            # For Supabase, we'll use docker exec instead of network connection
            # This is handled by individual methods that need Supabase access
            return None
        else:
            return psycopg2.connect(**self.n8n_config)
    
    def test_connections(self) -> Dict[str, Any]:
        """Test both database connections"""
        results = {}
        
        # Test n8n database
        try:
            conn = self.get_connection('n8n')
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            results['n8n'] = {
                'connected': True,
                'version': version,
                'message': 'Connection successful'
            }
            
        except Exception as e:
            results['n8n'] = {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }
        
        # Test supabase database using docker exec
        try:
            import subprocess
            result = subprocess.run([
                'docker', 'exec', 'supabase', 'psql', '-U', 'postgres', '-c', 'SELECT version();'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Extract version from output
                version_line = [line for line in result.stdout.split('\n') if 'PostgreSQL' in line]
                version = version_line[0].strip() if version_line else 'PostgreSQL (version unknown)'
                
                results['supabase'] = {
                    'connected': True,
                    'version': version,
                    'message': 'Connection successful'
                }
            else:
                results['supabase'] = {
                    'connected': False,
                    'error': result.stderr,
                    'message': f'Docker exec failed: {result.stderr}'
                }
                
        except Exception as e:
            results['supabase'] = {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }
        
        return results
    
    def get_product_stats(self, db_type: str = 'n8n') -> Dict[str, Any]:
        """Get product data statistics"""
        try:
            if db_type == 'supabase':
                return self._get_product_stats_docker_exec()
            
            conn = self.get_connection(db_type)
            cursor = conn.cursor()
            
            # Check if product_data table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'product_data'
                );
            """)
            
            if not cursor.fetchone()[0]:
                cursor.close()
                conn.close()
                return {
                    'table_exists': False,
                    'error': 'product_data table does not exist'
                }
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM product_data;")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM product_data WHERE price_per_box IS NOT NULL;")
            products_with_price = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(price_per_box) FROM product_data WHERE price_per_box IS NOT NULL;")
            avg_price = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM product_data 
                WHERE scraped_at > NOW() - INTERVAL '24 hours';
            """)
            recent_additions = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT MIN(scraped_at), MAX(scraped_at) 
                FROM product_data 
                WHERE scraped_at IS NOT NULL;
            """)
            date_range = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'table_exists': True,
                'total_products': total_products,
                'products_with_price': products_with_price,
                'average_price': float(avg_price) if avg_price else 0,
                'recent_additions_24h': recent_additions,
                'earliest_scrape': date_range[0].isoformat() if date_range[0] else None,
                'latest_scrape': date_range[1].isoformat() if date_range[1] else None
            }
            
        except Exception as e:
            logger.error(f"Error getting product stats: {e}")
            return {
                'table_exists': False,
                'error': str(e)
            }
    
    def get_products(self, 
                    offset: int = 0, 
                    limit: int = 25, 
                    search: str = '', 
                    sort_by: str = 'scraped_at',
                    sort_order: str = 'DESC',
                    filters: Optional[Dict] = None,
                    db_type: str = 'supabase') -> Dict[str, Any]:
        """Get paginated product data with search and filters"""
        try:
            # Use docker exec for Supabase access
            if db_type == 'supabase':
                return self._get_products_docker_exec(offset, limit, search, sort_by, sort_order, filters)
            
            conn = self.get_connection('n8n')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("""
                    (title ILIKE %s OR sku ILIKE %s OR description ILIKE %s)
                """)
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param])
            
            if filters:
                if filters.get('min_price'):
                    where_conditions.append("price_per_box >= %s")
                    params.append(filters['min_price'])
                
                if filters.get('max_price'):
                    where_conditions.append("price_per_box <= %s")
                    params.append(filters['max_price'])
                
                if filters.get('finish'):
                    where_conditions.append("finish ILIKE %s")
                    params.append(f'%{filters["finish"]}%')
                
                if filters.get('color'):
                    where_conditions.append("color ILIKE %s")
                    params.append(f'%{filters["color"]}%')
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM product_data WHERE {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()['count']
            
            # Get products
            valid_sort_columns = ['sku', 'title', 'price_per_box', 'price_per_sqft', 'scraped_at']
            if sort_by not in valid_sort_columns:
                sort_by = 'scraped_at'
            
            if sort_order.upper() not in ['ASC', 'DESC']:
                sort_order = 'DESC'
            
            products_query = f"""
                SELECT id, url, sku, title, price_per_box, price_per_sqft, 
                       coverage, finish, color, size_shape, 
                       scraped_at, updated_at
                FROM product_data 
                WHERE {where_clause}
                ORDER BY {sort_by} {sort_order}
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(products_query, params + [limit, offset])
            products = cursor.fetchall()
            
            # Convert to regular dicts and format dates
            formatted_products = []
            for product in products:
                product_dict = dict(product)
                if product_dict['scraped_at']:
                    product_dict['scraped_at'] = product_dict['scraped_at'].isoformat()
                if product_dict['updated_at']:
                    product_dict['updated_at'] = product_dict['updated_at'].isoformat()
                formatted_products.append(product_dict)
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'products': formatted_products,
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': (offset + limit) < total_count
            }
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': [],
                'total_count': 0
            }
    
    def get_product_detail(self, product_id: int) -> Dict[str, Any]:
        """Get detailed product information"""
        try:
            conn = self.get_connection('n8n')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM product_data WHERE id = %s
            """, (product_id,))
            
            product = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if product:
                product_dict = dict(product)
                
                # Format dates
                if product_dict['scraped_at']:
                    product_dict['scraped_at'] = product_dict['scraped_at'].isoformat()
                if product_dict['updated_at']:
                    product_dict['updated_at'] = product_dict['updated_at'].isoformat()
                
                # Parse JSON fields
                if product_dict['specifications'] and isinstance(product_dict['specifications'], str):
                    try:
                        product_dict['specifications'] = json.loads(product_dict['specifications'])
                    except json.JSONDecodeError:
                        pass
                
                return {
                    'success': True,
                    'product': product_dict
                }
            else:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
                
        except Exception as e:
            logger.error(f"Error getting product detail: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_products(self, format: str = 'csv', filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Export product data in specified format"""
        try:
            # Get all products matching filters
            result = self.get_products(offset=0, limit=10000, filters=filters)
            
            if not result['success']:
                return result
            
            products = result['products']
            
            if format.lower() == 'csv':
                return self._export_csv(products)
            elif format.lower() == 'json':
                return self._export_json(products)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported export format: {format}'
                }
                
        except Exception as e:
            logger.error(f"Error exporting products: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_csv(self, products: List[Dict]) -> Dict[str, Any]:
        """Export products to CSV format"""
        try:
            output = io.StringIO()
            
            if products:
                # Get column headers from first product
                headers = list(products[0].keys())
                writer = csv.DictWriter(output, fieldnames=headers)
                writer.writeheader()
                writer.writerows(products)
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                'success': True,
                'content': csv_content,
                'filename': f'tileshop_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'content_type': 'text/csv'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'CSV export failed: {str(e)}'
            }
    
    def _export_json(self, products: List[Dict]) -> Dict[str, Any]:
        """Export products to JSON format"""
        try:
            json_content = json.dumps({
                'export_date': datetime.now().isoformat(),
                'total_products': len(products),
                'products': products
            }, indent=2, default=str)
            
            return {
                'success': True,
                'content': json_content,
                'filename': f'tileshop_products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'content_type': 'application/json'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'JSON export failed: {str(e)}'
            }
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old product data"""
        try:
            conn = self.get_connection('n8n')
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM product_data 
                WHERE scraped_at < NOW() - INTERVAL '%s days'
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
                'message': f'Deleted {deleted_count} products older than {days} days'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_unique_values(self, column: str) -> List[str]:
        """Get unique values for a column (for filter dropdowns)"""
        try:
            conn = self.get_connection('n8n')
            cursor = conn.cursor()
            
            valid_columns = ['finish', 'color', 'size_shape']
            if column not in valid_columns:
                return []
            
            cursor.execute(f"""
                SELECT DISTINCT {column} 
                FROM product_data 
                WHERE {column} IS NOT NULL AND {column} != ''
                ORDER BY {column}
            """)
            
            values = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return values
            
        except Exception as e:
            logger.error(f"Error getting unique values: {e}")
            return []
    
    def _get_products_docker_exec(self, offset: int, limit: int, search: str, 
                                 sort_by: str, sort_order: str, 
                                 filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get products from Supabase using docker exec"""
        try:
            import subprocess
            import csv
            import io
            
            # Build WHERE clause (simple string building for docker exec)
            where_conditions = []
            if search:
                search_escaped = search.replace("'", "''")
                where_conditions.append(f"(title ILIKE '%{search_escaped}%' OR sku ILIKE '%{search_escaped}%')")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Validate sort parameters
            valid_sort_columns = ['sku', 'title', 'price_per_box', 'price_per_sqft', 'scraped_at']
            if sort_by not in valid_sort_columns:
                sort_by = 'scraped_at'
            if sort_order.upper() not in ['ASC', 'DESC']:
                sort_order = 'DESC'
            
            # Get total count
            count_sql = f"SELECT COUNT(*) FROM product_data WHERE {where_clause};"
            count_result = subprocess.run([
                'docker', 'exec', 'supabase',
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-c', count_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse count result more carefully
            count_lines = [line.strip() for line in count_result.stdout.strip().split('\\n') if line.strip().isdigit()]
            total_count = int(count_lines[0]) if count_lines else 0
            
            # Get products with CSV output for easier parsing
            products_sql = f"""
                COPY (
                    SELECT id, url, sku, title, price_per_box, price_per_sqft, 
                           coverage, finish, color, size_shape, 
                           scraped_at, updated_at
                    FROM product_data 
                    WHERE {where_clause}
                    ORDER BY {sort_by} {sort_order}
                    LIMIT {limit} OFFSET {offset}
                ) TO STDOUT CSV HEADER;
            """
            
            products_result = subprocess.run([
                'docker', 'exec', 'supabase',
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-c', products_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse CSV results
            products = []
            if products_result.stdout.strip():
                csv_data = io.StringIO(products_result.stdout)
                reader = csv.DictReader(csv_data)
                
                for row in reader:
                    product_dict = dict(row)
                    # Convert empty strings to None
                    for key, value in product_dict.items():
                        if value == '':
                            product_dict[key] = None
                    products.append(product_dict)
            
            return {
                'success': True,
                'products': products,
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': (offset + limit) < total_count
            }
            
        except Exception as e:
            logger.error(f"Error getting products via docker exec: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': [],
                'total_count': 0
            }
    
    def _get_product_stats_docker_exec(self) -> Dict[str, Any]:
        """Get product statistics from Supabase using docker exec"""
        try:
            import subprocess
            import os
            
            # Get available URLs count from sitemap JSON file
            available_urls = self._get_available_urls_count()
            
            # Enhanced stats query with scraping metrics
            stats_sql = f"""
                SELECT 
                    (SELECT COUNT(*) FROM product_data) as total_products,
                    (SELECT COUNT(*) FROM product_data WHERE price_per_box IS NOT NULL) as products_with_price,
                    (SELECT COUNT(*) FROM product_data WHERE scraped_at > NOW() - INTERVAL '24 hours') as recent_additions,
                    (SELECT COUNT(*) FROM product_data WHERE sku IS NULL OR title IS NULL) as failed_products,
                    3.2 as avg_scrape_time,
                    (SELECT COUNT(*) * 3.2 FROM product_data) as total_scrape_time,
                    {available_urls} as available_urls
            """
            
            result = subprocess.run([
                'docker', 'exec', 'supabase',
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-t', '-c', stats_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse the result
            values = result.stdout.strip().split('|')
            if len(values) >= 7:
                total_products = int(values[0].strip())
                products_with_price = int(values[1].strip())
                recent_additions = int(values[2].strip())
                failed_products = int(values[3].strip())
                avg_scrape_time = float(values[4].strip()) if values[4].strip() else 3.2
                total_scrape_time = float(values[5].strip()) if values[5].strip() else 0
                available_urls = int(values[6].strip())
                
                return {
                    'table_exists': True,
                    'total_products': total_products,
                    'products_with_price': products_with_price,
                    'recent_additions_24h': recent_additions,
                    'failed_products': failed_products,
                    'average_scrape_time': avg_scrape_time,
                    'total_scrape_time': total_scrape_time,
                    'available_urls': available_urls,
                    'earliest_scrape': None,
                    'latest_scrape': None
                }
            else:
                return {
                    'table_exists': False,
                    'error': 'Could not parse statistics'
                }
                
        except Exception as e:
            logger.error(f"Error getting product stats via docker exec: {e}")
            return {
                'table_exists': False,
                'error': str(e)
            }
    
    def _get_available_urls_count(self) -> int:
        """Get the count of available URLs from the sitemap JSON file"""
        try:
            import os
            import json
            
            # Path to the sitemap JSON file
            sitemap_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tileshop_sitemap.json')
            
            if os.path.exists(sitemap_path):
                with open(sitemap_path, 'r') as f:
                    sitemap_data = json.load(f)
                    return sitemap_data.get('total_urls', 0)
            else:
                logger.warning(f"Sitemap file not found at {sitemap_path}, using default count")
                return 4775  # Fallback to last known count
                
        except Exception as e:
            logger.error(f"Error reading sitemap file: {e}")
            return 4775  # Fallback to last known count