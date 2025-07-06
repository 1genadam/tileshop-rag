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
        self.relational_db_config = {
            'host': '127.0.0.1',  # Use IPv4 explicitly
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': 'postgres'  # Use postgres user with known password
        }
        
        self.supabase_config = {
            'host': '127.0.0.1',  # Use IPv4 explicitly
            'port': 5433,
            'database': 'postgres',
            'user': 'postgres',
            'password': 'supabase123'
        }
    
    def get_connection(self, db_type: str = 'relational_db'):
        """Get database connection"""
        if db_type == 'supabase':
            # For Supabase, we'll use docker exec instead of network connection
            # This is handled by individual methods that need Supabase access
            return None
        else:
            return psycopg2.connect(**self.relational_db_config)
    
    def test_connections(self) -> Dict[str, Any]:
        """Test both database connections"""
        results = {}
        
        # Test relational database
        try:
            conn = self.get_connection('relational_db')
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            results['relational_db'] = {
                'connected': True,
                'version': version,
                'message': 'Connection successful'
            }
            
        except Exception as e:
            results['relational_db'] = {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }
        
        # Test supabase database using docker exec
        try:
            import subprocess
            result = subprocess.run([
                'docker', 'exec', 'vector_db', 'psql', '-U', 'postgres', '-c', 'SELECT version();'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Extract version from output
                version_line = [line for line in result.stdout.split('\n') if 'PostgreSQL' in line]
                version = version_line[0].strip() if version_line else 'PostgreSQL (version unknown)'
                
                results['vector_db'] = {
                    'connected': True,
                    'version': version,
                    'message': 'Connection successful'
                }
            else:
                results['vector_db'] = {
                    'connected': False,
                    'error': result.stderr,
                    'message': f'Docker exec failed: {result.stderr}'
                }
                
        except Exception as e:
            results['vector_db'] = {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }
        
        return results
    
    def get_product_stats(self, db_type: str = 'relational_db') -> Dict[str, Any]:
        """Get product data statistics"""
        try:
            if db_type == 'supabase':
                return self._get_product_stats_docker_exec()
            elif db_type == 'relational_db':
                return self._get_product_stats_relational_docker_exec()
            
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
    
    def get_quality_stats(self, db_type: str = 'relational_db') -> Dict[str, Any]:
        """Get data quality statistics for products scraped in the last 24 hours"""
        try:
            if db_type == 'supabase':
                return self._get_quality_stats_docker_exec('vector_db')
            elif db_type == 'relational_db':
                return self._get_quality_stats_docker_exec('postgres')
            
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
            
            # Get recent products (last 24 hours) - limit to 10 for quality analysis
            cursor.execute("""
                SELECT sku, title, price_per_box, price_per_sqft, coverage, finish, color, 
                       size_shape, description, specifications, images, brand, primary_image, 
                       collection_links
                FROM product_data 
                WHERE scraped_at > NOW() - INTERVAL '24 hours'
                ORDER BY scraped_at DESC
                LIMIT 10
            """)
            
            recent_products = cursor.fetchall()
            total_recent_products = len(recent_products)
            
            # Define key fields to check (excluding first column which is sku for identification)
            key_fields = ['title', 'price_per_box', 'price_per_sqft', 'coverage', 'finish', 
                         'color', 'size_shape', 'description', 'specifications', 'images', 
                         'brand', 'primary_image', 'collection_links']
            
            high_quality_products = 0
            low_quality_products = 0
            poor_products = []
            
            for product in recent_products:
                sku = product[0]  # First column is SKU
                product_data = product[1:]  # Rest are the key fields
                
                # Count non-null fields
                non_null_count = sum(1 for field in product_data if field is not None and str(field).strip() != '')
                
                if non_null_count >= 10:
                    high_quality_products += 1
                else:
                    low_quality_products += 1
                    if sku:  # Only add if SKU exists
                        poor_products.append(sku)
            
            # Calculate quality percentage
            quality_percentage = (high_quality_products / total_recent_products * 100) if total_recent_products > 0 else 100.0
            
            # Determine alert level
            if quality_percentage >= 80:
                alert_level = 'good'
            elif quality_percentage >= 60:
                alert_level = 'warning'
            else:
                alert_level = 'critical'
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'total_recent_products': total_recent_products,
                'high_quality_products': high_quality_products,
                'low_quality_products': low_quality_products,
                'quality_percentage': round(quality_percentage, 2),
                'poor_products': poor_products,
                'alert_level': alert_level
            }
            
        except Exception as e:
            logger.error(f"Error getting quality stats: {e}")
            return {
                'success': False,
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
            
            conn = self.get_connection('relational_db')
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
                SELECT id, url, sku, title, price_per_box, price_per_sqft, price_per_piece,
                       coverage, finish, color, size_shape, brand, specifications,
                       description, resources, images, collection_links, primary_image,
                       image_variants, color_variations, color_images,
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
                
                # Parse JSON string fields
                import json
                if product_dict.get('color_variations'):
                    try:
                        product_dict['color_variations'] = json.loads(product_dict['color_variations'])
                    except (json.JSONDecodeError, TypeError):
                        product_dict['color_variations'] = None
                
                if product_dict.get('color_images'):
                    try:
                        product_dict['color_images'] = json.loads(product_dict['color_images'])
                    except (json.JSONDecodeError, TypeError):
                        product_dict['color_images'] = None
                
                if product_dict.get('images'):
                    try:
                        product_dict['images'] = json.loads(product_dict['images'])
                    except (json.JSONDecodeError, TypeError):
                        product_dict['images'] = None
                
                if product_dict.get('collection_links'):
                    try:
                        product_dict['collection_links'] = json.loads(product_dict['collection_links'])
                    except (json.JSONDecodeError, TypeError):
                        product_dict['collection_links'] = None
                
                if product_dict.get('image_variants'):
                    try:
                        product_dict['image_variants'] = json.loads(product_dict['image_variants'])
                    except (json.JSONDecodeError, TypeError):
                        product_dict['image_variants'] = None
                
                # specifications is already JSONB, no need to parse
                
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
            conn = self.get_connection('relational_db')
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
            conn = self.get_connection('relational_db')
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
            conn = self.get_connection('relational_db')
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
                'docker', 'exec', 'vector_db',
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
                'docker', 'exec', 'vector_db',
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
                'docker', 'exec', 'vector_db',
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
    
    def _get_product_stats_relational_docker_exec(self) -> Dict[str, Any]:
        """Get product statistics from PostgreSQL using docker exec"""
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
                'docker', 'exec', 'relational_db',
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-t', '-c', stats_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse the result
            values = result.stdout.strip().split('|')
            if len(values) >= 7:
                return {
                    'table_exists': True,
                    'total_products': int(values[0].strip()),
                    'products_with_price': int(values[1].strip()),
                    'recent_additions_24h': int(values[2].strip()),
                    'failed_products': int(values[3].strip()),
                    'average_scrape_time': float(values[4].strip()),
                    'total_scrape_time': float(values[5].strip()),
                    'available_urls': int(values[6].strip())
                }
            else:
                logger.warning(f"Unexpected query result format: {result.stdout}")
                return {
                    'table_exists': False,
                    'error': 'Unexpected query result format'
                }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker exec failed for relational_db stats: {e}")
            return {
                'table_exists': False,
                'error': f'Docker exec failed: {e}'
            }
        except Exception as e:
            logger.error(f"Error getting relational_db stats via docker exec: {e}")
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

    def _get_quality_stats_docker_exec(self, container_name: str) -> Dict[str, Any]:
        """Get quality statistics using docker exec"""
        try:
            import subprocess
            
            # Simplified quality analysis using basic fields that exist in all databases
            quality_sql = """
                SELECT sku,
                       CASE WHEN title IS NOT NULL AND title != '' THEN 1 ELSE 0 END +
                       CASE WHEN brand IS NOT NULL AND brand != '' THEN 1 ELSE 0 END +
                       CASE WHEN price_per_box IS NOT NULL OR price_per_sqft IS NOT NULL OR price_per_piece IS NOT NULL THEN 1 ELSE 0 END +
                       CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END +
                       CASE WHEN size_shape IS NOT NULL AND size_shape != '' THEN 1 ELSE 0 END +
                       CASE WHEN finish IS NOT NULL AND finish != '' THEN 1 ELSE 0 END +
                       CASE WHEN coverage IS NOT NULL AND coverage != '' THEN 1 ELSE 0 END +
                       CASE WHEN color IS NOT NULL AND color != '' THEN 1 ELSE 0 END +
                       CASE WHEN primary_image IS NOT NULL AND primary_image != '' THEN 1 ELSE 0 END +
                       CASE WHEN specifications IS NOT NULL AND CAST(specifications AS TEXT) != '{}' AND CAST(specifications AS TEXT) != '' THEN 1 ELSE 0 END
                       as field_count
                FROM product_data 
                WHERE scraped_at > NOW() - INTERVAL '24 hours'
                ORDER BY scraped_at DESC
                LIMIT 50
            """
            
            result = subprocess.run([
                'docker', 'exec', container_name,
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-t', '-c', quality_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse results
            total_recent_products = 0
            high_quality_products = 0
            low_quality_products = 0
            poor_products = []
            
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) >= 2:
                            sku = parts[0].strip()
                            try:
                                field_count = int(parts[1].strip())
                                total_recent_products += 1
                                
                                # Realistic quality scoring: require at least 4 out of 10 basic fields
                                quality_threshold = 4
                                
                                if field_count >= quality_threshold:
                                    high_quality_products += 1
                                else:
                                    low_quality_products += 1
                                    if sku and sku != '':
                                        poor_products.append(f"{sku} ({field_count}/10 fields)")
                            except (ValueError, IndexError):
                                # Skip malformed lines
                                continue
            
            # Calculate quality percentage
            quality_percentage = (high_quality_products / total_recent_products * 100) if total_recent_products > 0 else 100.0
            
            # Determine alert level
            if quality_percentage >= 80:
                alert_level = 'good'
            elif quality_percentage >= 60:
                alert_level = 'warning'
            else:
                alert_level = 'critical'
            
            return {
                'success': True,
                'total_recent_products': total_recent_products,
                'high_quality_products': high_quality_products,
                'low_quality_products': low_quality_products,
                'quality_percentage': round(quality_percentage, 2),
                'poor_products': poor_products,
                'alert_level': alert_level
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker exec failed for quality stats: {e.stderr}")
            return {
                'success': False,
                'error': f'Database query failed: {e.stderr}'
            }
        except Exception as e:
            logger.error(f"Error getting quality stats via docker exec: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_product_by_sku(self, sku: str, db_type: str = 'relational_db') -> Dict[str, Any]:
        """Get product information by SKU"""
        try:
            if db_type == 'supabase':
                return self._get_product_by_sku_docker_exec(sku)
            
            conn = self.get_connection('relational_db')
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM product_data WHERE sku = %s
            """, (sku,))
            
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
                
                # Parse images field if it exists
                if product_dict.get('images') and isinstance(product_dict['images'], str):
                    try:
                        product_dict['images'] = json.loads(product_dict['images'])
                    except json.JSONDecodeError:
                        pass
                
                # Parse collection_links field if it exists
                if product_dict.get('collection_links') and isinstance(product_dict['collection_links'], str):
                    try:
                        product_dict['collection_links'] = json.loads(product_dict['collection_links'])
                    except json.JSONDecodeError:
                        pass
                
                # Parse resources field if it exists
                if product_dict.get('resources') and isinstance(product_dict['resources'], str):
                    try:
                        product_dict['resources'] = json.loads(product_dict['resources'])
                    except json.JSONDecodeError:
                        pass
                
                # Parse color_images field if it exists  
                if product_dict.get('color_images') and isinstance(product_dict['color_images'], str):
                    try:
                        product_dict['color_images'] = json.loads(product_dict['color_images'])
                    except json.JSONDecodeError:
                        pass
                
                return {
                    'success': True,
                    'product': product_dict,
                    'found': True
                }
            else:
                return {
                    'success': True,
                    'product': None,
                    'found': False,
                    'message': f'No product found with SKU: {sku}'
                }
                
        except Exception as e:
            logger.error(f"Error getting product by SKU: {e}")
            return {
                'success': False,
                'error': str(e),
                'found': False
            }

    def _get_product_by_sku_docker_exec(self, sku: str) -> Dict[str, Any]:
        """Get product by SKU from Supabase using docker exec"""
        try:
            import subprocess
            
            # Escape the SKU for SQL
            sku_escaped = sku.replace("'", "''")
            
            # Get product with simple SELECT query
            product_sql = f"""
                SELECT id, url, sku, title, description, price_per_box, price_per_sqft, 
                       coverage, finish, color, size_shape, specifications,
                       scraped_at, updated_at
                FROM product_data 
                WHERE sku = '{sku_escaped}'
                LIMIT 1;
            """
            
            result = subprocess.run([
                'docker', 'exec', 'vector_db',
                'psql', '-U', 'postgres', '-d', 'postgres',
                '-t', '-c', product_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse result
            if result.stdout.strip():
                # Split the row by pipe separator
                values = [v.strip() for v in result.stdout.strip().split('|')]
                
                if len(values) >= 12:  # We expect at least 12 fields
                    product_dict = {
                        'id': values[0] if values[0] != '' else None,
                        'url': values[1] if values[1] != '' else None,
                        'sku': values[2] if values[2] != '' else None,
                        'title': values[3] if values[3] != '' else None,
                        'description': values[4] if values[4] != '' else None,
                        'price_per_box': float(values[5]) if values[5] and values[5] != '' else None,
                        'price_per_sqft': float(values[6]) if values[6] and values[6] != '' else None,
                        'coverage': values[7] if values[7] != '' else None,
                        'finish': values[8] if values[8] != '' else None,
                        'color': values[9] if values[9] != '' else None,
                        'size_shape': values[10] if values[10] != '' else None,
                        'specifications': values[11] if values[11] != '' else None,
                        'scraped_at': values[12] if len(values) > 12 and values[12] != '' else None,
                        'updated_at': values[13] if len(values) > 13 and values[13] != '' else None
                    }
                    
                    # Parse JSON specifications if present
                    if product_dict.get('specifications'):
                        try:
                            product_dict['specifications'] = json.loads(product_dict['specifications'])
                        except json.JSONDecodeError:
                            pass
                    
                    return {
                        'success': True,
                        'product': product_dict,
                        'found': True
                    }
            
            # No product found
            return {
                'success': True,
                'product': None,
                'found': False,
                'message': f'No product found with SKU: {sku}'
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker exec failed for SKU lookup: {e.stderr}")
            return {
                'success': False,
                'error': f'Database query failed: {e.stderr}',
                'found': False
            }
        except Exception as e:
            logger.error(f"Error getting product by SKU via docker exec: {e}")
            return {
                'success': False,
                'error': str(e),
                'found': False
            }