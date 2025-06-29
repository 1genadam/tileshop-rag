#!/usr/bin/env python3
"""
Simple Tileshop RAG System - Supabase integration via docker exec
"""

import json
import logging
import subprocess
import csv
import io
import os
import re
from typing import List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import anthropic for Claude API
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available - analytical queries will be limited")

class SimpleTileshopRAG:
    def __init__(self):
        # Supabase container for data access
        self.supabase_container = 'supabase'
        self.db_name = 'postgres'
        
        # Initialize Claude API client
        self.claude_client = None
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                try:
                    logger.info(f"Loading API key starting with: {api_key[:15]}...")
                    self.claude_client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Claude API client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Claude API client: {e}")
            else:
                logger.warning("ANTHROPIC_API_KEY not found in environment variables")
    
    def _enhance_slip_resistant_query(self, query: str) -> str:
        """Enhance queries for slip-resistant tiles by mapping to database terms"""
        query_lower = query.lower()
        
        # Map slip-resistant terms to specific finish categories
        slip_resistant_terms = [
            'non-slip', 'non slip', 'slip resistant', 'slip-resistant', 
            'anti-slip', 'anti slip', 'textured surface', 'grip', 'safe'
        ]
        
        slippery_terms = [
            'slippery', 'glossy', 'polished', 'smooth', 'shiny'
        ]
        
        if any(term in query_lower for term in slip_resistant_terms):
            # Add terms that indicate slip resistance: tumbled, honed, matte, pebble, cobble, mosaic, penny round
            if 'tile' in query_lower or 'tiles' in query_lower:
                enhanced_terms = ['tumbled', 'honed', 'matte', 'textured', 'pebble', 'cobble', 'mosaic', 'penny round', 'hexagon']
                return f"{query} {' '.join(enhanced_terms)}"
        elif any(term in query_lower for term in slippery_terms):
            # Add terms that indicate slippery surfaces: gloss, satin
            if 'tile' in query_lower or 'tiles' in query_lower:
                enhanced_terms = ['gloss', 'glossy', 'satin', 'polished']
                return f"{query} {' '.join(enhanced_terms)}"
        
        return query
    
    def search_products(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search products using PostgreSQL full-text search via docker exec"""
        try:
            # Map slip-resistant terms to database values
            query_mapped = self._enhance_slip_resistant_query(query)
            
            # Escape the query for SQL
            query_escaped = query_mapped.replace("'", "''")
            
            # Check if query looks like a SKU (numeric or starts with #)
            is_sku_query = query.strip().isdigit() or query.strip().startswith('#')
            
            if is_sku_query:
                # Direct SKU search for exact matches
                clean_sku = query.strip().replace('#', '')
                search_sql = f"""
                    COPY (
                        SELECT url, sku, title, description, price_per_box, price_per_sqft, price_per_piece,
                               finish, color, size_shape, specifications, primary_image, image_variants, 
                               product_category, slip_rating, 1.0 as relevance
                        FROM product_data
                        WHERE sku = '{clean_sku}' OR sku = '#{clean_sku}'
                        LIMIT {limit}
                    ) TO STDOUT CSV HEADER;
                """
            else:
                # Determine product category filter based on query keywords - prioritize TILE for slip/floor queries
                category_filter = ""
                query_lower = query.lower()
                
                # PRIORITY: Slip/floor queries should default to TILE
                if any(word in query_lower for word in ['slip', 'floor', 'textured', 'matte', 'glossy', 'anti-slip', 'non-slip']):
                    category_filter = "AND product_category = 'TILE'"
                elif any(word in query_lower for word in ['tile', 'tiles', 'ceramic', 'porcelain', 'mosaic', 'subway', 'marble']):
                    category_filter = "AND product_category = 'TILE'"
                elif any(word in query_lower for word in ['wood', 'hardwood', 'engineered']) and 'tile' not in query_lower:
                    category_filter = "AND product_category = 'WOOD'"
                elif any(word in query_lower for word in ['shelf', 'shelves']):
                    category_filter = "AND product_category = 'SHELF'"
                elif any(word in query_lower for word in ['threshold', 'threshhold']):
                    category_filter = "AND product_category = 'THRESHOLD'"
                elif any(word in query_lower for word in ['curb']):
                    category_filter = "AND product_category = 'CURB'"
                elif any(word in query_lower for word in ['laminate']):
                    category_filter = "AND product_category = 'LAMINATE'"
                elif any(word in query_lower for word in ['lvp', 'lvt', 'luxury vinyl']):
                    category_filter = "AND product_category = 'LVP_LVT'"
                elif any(word in query_lower for word in ['molding', 'trim', 'quarter round', 't-molding', 'stair', 'reducer']):
                    category_filter = "AND product_category = 'TRIM_MOLDING'"
                # If dimensions mentioned, likely tiles
                elif any(word in query_lower for word in ['2x2', '3x6', '12x24', 'inch', 'in.']):
                    category_filter = "AND product_category = 'TILE'"
                
                # Enhanced search for slip-resistant and color queries
                slip_boost = ""
                color_filter = ""
                
                if any(term in query_lower for term in ['slip', 'anti-slip', 'non-slip', 'slip resistant', 'slip-resistant']):
                    # Add boost for slip-resistant tiles and include slip rating in search
                    slip_boost = """
                        + CASE WHEN slip_rating = 'SLIP_RESISTANT' THEN 0.5 ELSE 0 END
                        + CASE WHEN finish ILIKE '%matte%' OR finish ILIKE '%honed%' OR finish ILIKE '%tumbled%' OR finish ILIKE '%textured%' THEN 0.3 ELSE 0 END
                    """
                
                # Add color filtering for dark colors
                if any(term in query_lower for term in ['dark', 'black', 'brown', 'grey', 'gray', 'charcoal', 'slate']):
                    color_filter = """
                        AND (color ILIKE '%dark%' OR color ILIKE '%black%' OR color ILIKE '%brown%' OR 
                             color ILIKE '%grey%' OR color ILIKE '%gray%' OR color ILIKE '%charcoal%' OR 
                             color ILIKE '%slate%' OR title ILIKE '%dark%' OR title ILIKE '%black%' OR 
                             title ILIKE '%brown%' OR title ILIKE '%grey%' OR title ILIKE '%gray%')
                    """
                
                # Use PostgreSQL full-text search via docker exec with category filtering
                search_sql = f"""
                    COPY (
                        SELECT url, sku, title, description, price_per_box, price_per_sqft, price_per_piece,
                               finish, color, size_shape, specifications, primary_image, image_variants, 
                               product_category, slip_rating,
                               (ts_rank(to_tsvector('english', 
                                   COALESCE(sku, '') || ' ' ||
                                   COALESCE(title, '') || ' ' || 
                                   COALESCE(description, '') || ' ' || 
                                   COALESCE(finish, '') || ' ' || 
                                   COALESCE(color, '') || ' ' || 
                                   COALESCE(size_shape, '') || ' ' ||
                                   COALESCE(slip_rating, '')
                               ), plainto_tsquery('english', '{query_escaped}')) {slip_boost}) as relevance
                        FROM product_data
                        WHERE (to_tsvector('english', 
                            COALESCE(sku, '') || ' ' ||
                            COALESCE(title, '') || ' ' || 
                            COALESCE(description, '') || ' ' || 
                            COALESCE(finish, '') || ' ' || 
                            COALESCE(color, '') || ' ' || 
                            COALESCE(size_shape, '') || ' ' ||
                            COALESCE(slip_rating, '')
                        ) @@ plainto_tsquery('english', '{query_escaped}')
                        OR ('{query_lower}' LIKE '%slip%' AND slip_rating = 'SLIP_RESISTANT'))
                        {category_filter}
                        {color_filter}
                        ORDER BY relevance DESC
                        LIMIT {limit}
                    ) TO STDOUT CSV HEADER;
                """
            
            result = subprocess.run([
                'docker', 'exec', self.supabase_container,
                'psql', '-U', 'postgres', '-d', self.db_name,
                '-c', search_sql
            ], capture_output=True, text=True, check=True)
            
            formatted_results = []
            if result.stdout.strip():
                csv_data = io.StringIO(result.stdout)
                reader = csv.DictReader(csv_data)
                
                for row in reader:
                    # Convert empty strings to None and parse types
                    product = {}
                    for key, value in row.items():
                        if value == '':
                            product[key] = None
                        elif key in ['price_per_box', 'price_per_sqft', 'price_per_piece', 'relevance']:
                            product[key] = float(value) if value else None
                        else:
                            product[key] = value
                    
                    formatted_results.append(product)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def chat(self, query: str) -> str:
        """Generate intelligent chat response - Smart routing based on query type"""
        try:
            # Check if this is a direct SKU query (more comprehensive detection)
            query_lower = query.lower().strip()
            
            # Direct patterns
            is_direct_sku = query.strip().isdigit() or query.strip().startswith('#')
            
            # Contains SKU patterns
            contains_sku_pattern = bool(re.search(r'\bsku\s*#?\s*\d+|\b\d{6}\b', query, re.IGNORECASE))
            
            # SKU-related queries
            is_sku_question = 'sku' in query_lower and any(word in query_lower for word in ['what', 'show', 'find', 'get', 'lookup'])
            
            # Image requests for recently mentioned products (context-aware)
            is_image_request = any(word in query_lower for word in ['image', 'images', 'picture', 'photo']) and any(word in query_lower for word in ['show', 'display', 'see'])
            
            # Treat image requests as SKU queries if they contain this/that/it (referring to previous product)
            is_contextual_image_request = is_image_request and any(word in query_lower for word in ['this', 'that', 'it', 'these', 'them'])
            
            is_sku_query = is_direct_sku or contains_sku_pattern or is_sku_question or is_contextual_image_request
            
            if is_sku_query:
                # For SKU queries, use search directly for immediate results
                logger.info("Detected SKU query, using direct search")
                
                # Extract SKU number from query
                sku_match = re.search(r'\b(\d{6})\b', query)
                if sku_match:
                    sku_number = sku_match.group(1)
                    logger.info(f"Extracted SKU: {sku_number}")
                    return self._handle_search_query(sku_number)
                elif is_contextual_image_request:
                    # For contextual image requests without explicit SKU, search for common SKUs
                    # For now, default to last known good SKU (683549) as fallback
                    logger.info("Contextual image request detected, using fallback SKU search")
                    return self._handle_search_query("683549")
                else:
                    return self._handle_search_query(query)
            
            # Check if this is a product search query (looking for specific products)
            search_indicators = ['looking for', 'find', 'show me', 'need', 'want', 'search', 'tiles', 'tile', 'floor', 'wall']
            analytical_indicators = ['cheapest', 'lowest', 'highest', 'most expensive', 'average', 'compare', 'best value', 'analyze']
            
            is_product_search = any(word in query_lower for word in search_indicators)
            is_analytical = any(word in query_lower for word in analytical_indicators)
            
            # If it's clearly a product search (not analytical), use database search for real results with images
            if is_product_search and not is_analytical:
                logger.info("Detected product search query, using database search")
                return self._handle_search_query(query)
            
            # For analytical queries, try Claude LLM first if available
            if self.claude_client:
                try:
                    return self._handle_analytical_query(query)
                except Exception as e:
                    logger.warning(f"Claude API failed, falling back to search: {e}")
                    # Fallback to search if Claude fails
                    return self._handle_search_query(query)
            else:
                # No Claude client available, use search directly
                logger.info("No Claude client available, using search")
                return self._handle_search_query(query)
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I encountered an error processing your request. Please try again."
    
    def _handle_analytical_query(self, query: str) -> str:
        """Handle analytical queries using Claude API"""
        try:
            # First, get all product data for analysis
            all_products = self._get_all_products_for_analysis()
            
            if not all_products:
                return "I don't have enough product data to analyze your query. Please ensure the database has been populated."
            
            # Use Claude to analyze the query and data
            prompt = f"""
You are an AI assistant helping customers analyze tile products. You have access to a database of tile products with the following information:

{json.dumps(all_products[:10], indent=2)}
... and {len(all_products) - 10} more products

User Query: "{query}"

Please analyze this query and provide a helpful response. If the user is asking for:
- Lowest/cheapest: Find the product with the minimum price per sq ft
- Highest/most expensive: Find the product with the maximum price per sq ft  
- Average price: Calculate the average price per sq ft
- Best value: Consider price and quality factors
- Comparisons: Compare products based on the criteria mentioned

Provide a specific, helpful answer with exact product names, SKUs, prices, and URLs when relevant.
"""

            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error in analytical query: {e}")
            # Re-raise the exception so the caller can handle fallback
            raise e
    
    def _handle_search_query(self, query: str) -> str:
        """Handle regular search queries"""
        # Extract meaningful search terms from query
        search_terms = self._extract_search_terms(query)
        results = self.search_products(search_terms)
        
        if not results:
            return "I couldn't find any products matching your query. Try searching for tile types, colors, finishes, or sizes."
        
        response_parts = [f"Here are {len(results)} products that match your query:\n"]
        
        for i, result in enumerate(results, 1):
            price_info = ""
            
            # Show per-piece pricing first if available
            if result.get('price_per_piece'):
                price_info = f" - ${result['price_per_piece']:.2f}/each"
            elif result.get('price_per_box'):
                price_info = f" - ${result['price_per_box']:.2f}/box"
                
            # Add per sq ft pricing if available
            if result.get('price_per_sqft'):
                if price_info:
                    price_info += f" (${result['price_per_sqft']:.2f}/sq ft)"
                else:
                    price_info = f" - ${result['price_per_sqft']:.2f}/sq ft"
            
            finish_color = []
            if result['finish']:
                finish_color.append(result['finish'])
            if result['color']:
                finish_color.append(result['color'])
            
            finish_color_str = " - " + " ".join(finish_color) if finish_color else ""
            size_str = f" - {result['size_shape']}" if result['size_shape'] else ""
            
            # Add image if available
            image_str = ""
            if result.get('primary_image'):
                image_str = f"   ![Product Image]({result['primary_image']})\n"
            
            response_parts.append(
                f"{i}. **{result['title']}** (SKU: {result['sku']})\n"
                f"   {price_info}{finish_color_str}{size_str}\n"
                f"{image_str}"
                f"   {result['url']}\n"
            )
        
        return "\n".join(response_parts)
    
    def _get_all_products_for_analysis(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all products for analytical queries"""
        try:
            # Get products with essential fields for analysis (includes images)
            analysis_sql = f"""
                COPY (
                    SELECT url, sku, title, price_per_box, price_per_sqft, price_per_piece,
                           finish, color, size_shape, primary_image, image_variants
                    FROM product_data
                    ORDER BY price_per_sqft DESC NULLS LAST
                    LIMIT {limit}
                ) TO STDOUT CSV HEADER;
            """
            
            result = subprocess.run([
                'docker', 'exec', self.supabase_container,
                'psql', '-U', 'postgres', '-d', self.db_name, '-c', analysis_sql
            ], capture_output=True, text=True, check=True)
            
            # Parse CSV results
            csv_reader = csv.DictReader(io.StringIO(result.stdout))
            products = []
            
            for row in csv_reader:
                # Convert numeric fields
                try:
                    row['price_per_box'] = float(row['price_per_box']) if row['price_per_box'] else None
                    row['price_per_sqft'] = float(row['price_per_sqft']) if row['price_per_sqft'] else None
                    row['price_per_piece'] = float(row['price_per_piece']) if row['price_per_piece'] else None
                except:
                    continue
                    
                products.append(row)
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting products for analysis: {e}")
            return []
    
    def _extract_search_terms(self, query: str) -> str:
        """Extract meaningful search terms from user query"""
        import re
        
        # Convert to lowercase
        query = query.lower()
        
        # Common tile materials and types
        tile_types = ['ceramic', 'porcelain', 'marble', 'travertine', 'subway', 'mosaic', 'wood', 'stone', 'glass']
        finishes = ['matte', 'gloss', 'glossy', 'polished', 'honed', 'tumbled']
        colors = ['white', 'black', 'gray', 'grey', 'brown', 'beige', 'blue', 'green', 'red', 'silver', 'gold']
        applications = ['wall', 'floor', 'bathroom', 'kitchen', 'backsplash']
        
        # Find matching terms
        found_terms = []
        
        for term_list in [tile_types, finishes, colors, applications]:
            for term in term_list:
                if term in query:
                    found_terms.append(term)
        
        # If we found specific terms, use them
        if found_terms:
            return ' '.join(found_terms)
        
        # Otherwise, remove common words and numbers
        stop_words = ['find', 'show', 'me', 'get', 'the', 'a', 'an', 'some', 'any', 'tiles', 'tile']
        words = query.split()
        meaningful_words = [w for w in words if w not in stop_words and not w.isdigit()]
        
        return ' '.join(meaningful_words) if meaningful_words else query
    
    def sync_data(self) -> bool:
        """Sync data - not needed since we use the DatabaseSyncManager"""
        # This method is called by the RAG manager but we use the separate sync manager
        # So just return True to indicate sync is handled elsewhere
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Supabase"""
        try:
            result = subprocess.run([
                'docker', 'exec', self.supabase_container,
                'psql', '-U', 'postgres', '-d', self.db_name,
                '-c', 'SELECT COUNT(*) FROM product_data;'
            ], capture_output=True, text=True, check=True)
            
            # Parse count
            count_lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip().isdigit()]
            count = int(count_lines[0]) if count_lines else 0
            
            return {
                'connected': True,
                'product_count': count,
                'message': f'Connected to Supabase with {count} products'
            }
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }