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

# Try to import OpenAI for embedding generation
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available - vector search will be limited")

class SimpleTileShopRAG:
    def __init__(self):
        # Vector database container for data access
        self.supabase_container = 'vector_db'
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
        
        # Initialize OpenAI client for embeddings
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
            else:
                logger.warning("OPENAI_API_KEY not found in environment variables")
    
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
    
    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query using OpenAI API"""
        try:
            if not self.openai_client:
                logger.warning("OpenAI client not available for embedding generation")
                return None
            
            # Generate embedding using OpenAI's text-embedding-3-small model
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def detect_subway_tile_query(self, query: str) -> Dict[str, Any]:
        """Enhanced detection for subway tile opportunities"""
        subway_indicators = ['subway', '3x6', '4x8', 'backsplash', 'bathroom wall', 'kitchen wall']
        project_indicators = ['bathroom', 'kitchen', 'shower', 'backsplash', 'remodel']
        
        query_lower = query.lower()
        
        # Detect both product interest AND project context
        return {
            'is_subway_query': any(term in query_lower for term in subway_indicators),
            'project_context': [term for term in project_indicators if term in query_lower],
            'needs_upselling': any(term in query_lower for term in subway_indicators)
        }
    
    def extract_project_scope(self, query: str) -> Dict[str, Any]:
        """Intelligent project scope detection"""
        query_lower = query.lower()
        
        # Extract room mentions
        room_indicators = {
            'bathroom': {'typical_size': '50-80 sq ft', 'high_moisture': True},
            'kitchen backsplash': {'typical_size': '30-50 sq ft', 'moderate_moisture': True},
            'shower': {'typical_size': '100-150 sq ft walls', 'high_moisture': True}
        }
        
        detected_room = None
        for room in room_indicators:
            if room.replace(' backsplash', '') in query_lower:
                detected_room = room
                break
        
        # Extract size if mentioned
        size_match = re.search(r'(\d+)\s*(?:sq\s*ft|square\s*feet)', query_lower)
        size = int(size_match.group(1)) if size_match else None
        
        return {
            'room_type': detected_room,
            'size': size,
            'room_info': room_indicators.get(detected_room, {}),
            'needs_size_followup': detected_room and not size
        }
    
    def calculate_material_needs(self, tile_selection: Dict, room_size: int, room_type: str) -> Dict[str, Any]:
        """Calculate complete project materials based on room size and type"""
        
        # Base tile calculations
        tile_cost = tile_selection.get('price_per_sqft', 0) * room_size
        boxes_needed = max(1, (room_size / 10.76))  # Typical coverage per box
        
        # Essential materials
        essential_package = {
            'grout': {
                'item': 'Sanded grout (1/8" spacing)',
                'cost': 17.0,
                'coverage': '40-200 sq ft per bag'
            },
            'thinset': {
                'item': 'Modified thinset',
                'cost': 30.0,
                'bags_needed': 1 if room_type not in ['bathroom', 'shower'] else 2,
                'note': 'Double quantity for membrane installations'
            },
            'tools': {
                'item': 'Basic installation tools',
                'cost': 65.0,
                'includes': '1/4" trowel + grout float + spacers'
            }
        }
        
        # Wet area additions
        if room_type in ['bathroom', 'shower']:
            essential_package.update({
                'waterproofing': {
                    'item': 'Backer-lite membrane (wet areas)',
                    'cost': 85.0,
                    'note': 'Essential for bathroom/shower floors'
                },
                'caulk': {
                    'item': '100% silicone caulk',
                    'cost': 12.0,
                    'note': 'Movement areas and transitions'
                },
                'sealer': {
                    'item': 'Grout sealer',
                    'cost': 25.0,
                    'note': 'Moisture protection'
                }
            })
        
        # Premium upgrades
        premium_options = {
            'trim_package': {
                'item': 'Matching trim and edging',
                'cost': 45.0,
                'note': 'Professional finishing'
            },
            'euro_trowel': {
                'item': 'Euro trowel (universal flexibility)',
                'cost': 85.0,
                'note': 'Handles any tile size perfectly'
            },
            'professional_tools': {
                'item': 'Complete tool kit',
                'cost': 150.0,
                'note': 'Everything needed for professional results'
            }
        }
        
        # Calculate totals
        essential_total = sum(item.get('cost', 0) * item.get('bags_needed', 1) for item in essential_package.values())
        premium_total = sum(item.get('cost', 0) for item in premium_options.values())
        
        return {
            'tile_info': {
                'cost': tile_cost,
                'boxes_needed': round(boxes_needed, 1),
                'coverage': f"{room_size} sq ft"
            },
            'essential_package': essential_package,
            'premium_options': premium_options,
            'pricing': {
                'tiles_only': tile_cost,
                'essential_total': tile_cost + essential_total,
                'premium_total': tile_cost + essential_total + premium_total
            }
        }
    
    def generate_upselling_response(self, subway_tiles: List[Dict], project_details: Dict, materials: Dict) -> str:
        """Generate compelling upselling response for subway tiles"""
        
        if not subway_tiles:
            return "I couldn't find subway tiles matching your query. Let me help you with other tile options."
        
        # Use first tile for primary recommendation
        primary_tile = subway_tiles[0]
        room_type = project_details.get('room_type', 'room')
        room_size = project_details.get('size', 50)  # Default 50 sq ft
        
        response_parts = [
            f"🏠 **Complete {room_type.replace('_', ' ').title()} Subway Tile Project**\n",
            f"**Your Selected Subway Tile:** {primary_tile['title']}",
            f"- **Base Cost:** ${materials['pricing']['tiles_only']:.2f} ({room_size} sq ft)",
            f"- **Coverage:** {materials['tile_info']['boxes_needed']} boxes\n",
            "🎯 **Essential Installation Materials:**"
        ]
        
        # Add essential materials
        for key, item in materials['essential_package'].items():
            cost = item['cost'] * item.get('bags_needed', 1)
            note = f" - {item.get('note', '')}" if item.get('note') else ""
            response_parts.append(f"✅ **{item['item'].title()}:** ${cost:.0f}{note}")
        
        response_parts.extend([
            "\n⭐ **Professional Upgrade Options:"
        ])
        
        # Add premium options
        for key, item in materials['premium_options'].items():
            note = f" - {item.get('note', '')}" if item.get('note') else ""
            response_parts.append(f"🔹 **{item['item'].title()}:** ${item['cost']:.0f}{note}")
        
        response_parts.extend([
            "\n💰 **Investment Summary:**",
            f"- **Tiles Only:** ${materials['pricing']['tiles_only']:.2f}",
            f"- **Essential Complete Package:** ${materials['pricing']['essential_total']:.2f}",
            f"- **Professional Complete Package:** ${materials['pricing']['premium_total']:.2f}\n",
            "🛡️ **Why Complete Packages Save Money:**",
            "- Prevents costly return trips for missing materials",
            "- Ensures proper installation and long-term performance",
            "- Professional tools create better results",
            "- Warranty protection with complete system approach\n",
            "Would you like me to customize this package for your specific project needs?"
        ])
        
        return "\n".join(response_parts)
    
    def search_products(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search products using vector similarity search with text fallback"""
        try:
            # Try vector search first
            vector_results = self.search_products_vector(query, limit)
            
            # If vector search returns results, use them
            if vector_results:
                logger.info(f"Vector search returned {len(vector_results)} results")
                return vector_results
            
            # Fallback to text search
            logger.info("Vector search returned no results, falling back to text search")
            return self._search_products_text_fallback(query, limit)
            
        except Exception as e:
            logger.error(f"Error in search_products: {e}")
            # Final fallback to text search
            return self._search_products_text_fallback(query, limit)
    
    def search_products_vector(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search products using vector similarity search via embeddings"""
        try:
            # Generate embedding for the search query
            query_embedding = self._generate_query_embedding(query)
            
            if not query_embedding:
                logger.warning("Could not generate embedding for query, falling back to text search")
                return self._search_products_text_fallback(query, limit)
            
            # Convert embedding to PostgreSQL array format
            embedding_str = '{' + ','.join(map(str, query_embedding)) + '}'
            
            # Use a simplified dot product for vector search (approximation of cosine similarity)
            # This is more efficient than full cosine similarity calculation
            search_sql = f"""
                COPY (
                    WITH query_embedding AS (
                        SELECT '{embedding_str}'::float[] as qemb
                    ),
                    similarity_scores AS (
                        SELECT 
                            pe.sku,
                            pe.title,
                            pe.content,
                            -- Calculate dot product similarity (normalized by query length)
                            (
                                SELECT SUM(
                                    (pe.embedding)[i] * (qe.qemb)[i]
                                ) / SQRT(
                                    (SELECT SUM(power((qe.qemb)[i], 2)) FROM generate_series(1, array_length(qe.qemb, 1)) i)
                                )
                                FROM generate_series(1, LEAST(array_length(pe.embedding, 1), array_length(qe.qemb, 1))) i,
                                     query_embedding qe
                            ) AS similarity_score
                        FROM product_embeddings pe, query_embedding qe
                        WHERE pe.embedding IS NOT NULL 
                          AND array_length(pe.embedding, 1) = array_length(qe.qemb, 1)
                    )
                    SELECT 
                        ss.sku,
                        ss.title,
                        ss.content,
                        ss.similarity_score,
                        -- Extract price and other details from content
                        CASE 
                            WHEN ss.content ~ '\\$[0-9]+\\.[0-9]+' THEN 
                                (regexp_matches(ss.content, '\\$([0-9]+\\.[0-9]+)', 'g'))[1]::decimal
                            ELSE NULL
                        END as price_estimate,
                        -- Extract size information
                        CASE 
                            WHEN ss.content ~ '[0-9]+ x [0-9]+ in\\.' THEN 
                                (regexp_matches(ss.content, '([0-9]+ x [0-9]+ in\\.)', 'g'))[1]
                            ELSE NULL
                        END as size_shape
                    FROM similarity_scores ss
                    WHERE ss.similarity_score > 0.1  -- Minimum similarity threshold
                    ORDER BY ss.similarity_score DESC
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
                        elif key in ['similarity_score', 'price_estimate']:
                            product[key] = float(value) if value else None
                        else:
                            product[key] = value
                    
                    formatted_results.append(product)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            # Fallback to text search if vector search fails
            return self._search_products_text_fallback(query, limit)
    
    def _search_products_text_fallback(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Fallback text search using product_embeddings table content"""
        try:
            # Split query into individual terms for better matching
            query_terms = query.lower().split()
            
            # Check if this is a price-filtered query
            price_filter = ""
            max_price = None
            if 'under' in query.lower() and any('$' in term or term.isdigit() for term in query_terms):
                # Extract price from query like "under 12$" or "under $12"
                import re
                price_match = re.search(r'under\s*\$?(\d+)', query.lower())
                if price_match:
                    max_price = float(price_match.group(1))
            
            # Create simpler WHERE clause with multiple terms
            where_conditions = []
            for term in query_terms:
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best'] and len(term) > 2:
                    # Escape single quotes for SQL
                    escaped_term = term.replace("'", "''")
                    where_conditions.append(f"(LOWER(title) LIKE '%{escaped_term}%' OR LOWER(content) LIKE '%{escaped_term}%')")
            
            if not where_conditions:
                return []
            
            where_clause = " OR ".join(where_conditions)
            
            # Check if this is a non-tile query (like LFT, thinset, mortar, grout)
            non_tile_terms = ['lft', 'thinset', 'mortar', 'adhesive', 'grout', 'sealer']
            is_non_tile_query = any(term in query.lower() for term in non_tile_terms)
            
            # Simple search with better relevance ordering
            # Create priority scoring for better ordering
            title_priority_conditions = []
            for term in query_terms:
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best'] and len(term) > 2:
                    escaped_term = term.replace("'", "''")
                    title_priority_conditions.append(f"LOWER(title) LIKE '%{escaped_term}%'")
            
            title_priority_clause = " OR ".join(title_priority_conditions) if title_priority_conditions else "FALSE"
            
            # Different filters for tile vs non-tile queries
            if is_non_tile_query:
                filter_clause = ""  # No tile requirement for installation materials
            else:
                filter_clause = """
                      AND LOWER(title) LIKE '%tile%'
                      AND NOT (LOWER(title) LIKE '%tool%' OR LOWER(title) LIKE '%grout%' OR 
                               LOWER(title) LIKE '%float%' OR LOWER(title) LIKE '%base%' OR
                               LOWER(title) LIKE '%wedge%' OR LOWER(title) LIKE '%spacer%')"""
            
            search_sql = f"""
                COPY (
                    SELECT 
                        sku,
                        title,
                        content,
                        'text_search' as search_type
                    FROM product_embeddings
                    WHERE ({where_clause}){filter_clause}
                    ORDER BY 
                        CASE WHEN ({title_priority_clause}) THEN 1 ELSE 2 END,
                        sku
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
                        else:
                            product[key] = value
                    
                    # Set relevance score for text search results
                    product['relevance_score'] = 1.0
                    formatted_results.append(product)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in text fallback search: {e}")
            return []
    
    def chat(self, query: str) -> str:
        """Generate intelligent chat response - Smart routing based on query type"""
        try:
            # Check for subway tile upselling opportunities FIRST
            subway_detection = self.detect_subway_tile_query(query)
            
            if subway_detection['is_subway_query'] and subway_detection['needs_upselling']:
                logger.info("Detected subway tile upselling opportunity")
                return self._handle_subway_upselling_query(query)
            
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
            search_indicators = ['looking for', 'find', 'show me', 'need', 'want', 'search', 'tiles', 'tile', 'floor', 'wall', 'tell me about', 'what is', 'lft', 'thinset', 'mortar']
            analytical_indicators = ['cheapest', 'lowest', 'highest', 'most expensive', 'average', 'compare', 'best value', 'analyze']
            
            is_product_search = any(word in query_lower for word in search_indicators)
            is_analytical = any(word in query_lower for word in analytical_indicators)
            
            # Override: If it's asking about specific products (LFT, etc.), treat as product search
            specific_products = ['lft', 'thinset', 'mortar', 'grout', 'sealer', 'adhesive']
            if any(product in query_lower for product in specific_products):
                is_product_search = True
                is_analytical = False
            
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
    
    def _handle_subway_upselling_query(self, query: str) -> str:
        """Handle subway tile queries with upselling logic"""
        try:
            # Search for subway tiles using simplified search
            subway_tiles = self.search_products("subway", limit=3)
            
            if not subway_tiles:
                return "I couldn't find subway tiles matching your query. Let me search for other tile options."
            
            # Extract project details
            project_details = self.extract_project_scope(query)
            
            # If no room size, ask for it
            if project_details['needs_size_followup']:
                room_type = project_details['room_type'].replace('_', ' ')
                return f"""I'd love to help you create a complete {room_type} subway tile project! 
                
**Found These Subway Tiles:**
{self._format_tile_results(subway_tiles[:2])}

To calculate exact materials and create your complete project package, what size area are you tiling? 
For example:
- Small bathroom: 50 sq ft
- Large bathroom: 80+ sq ft  
- Kitchen backsplash: 30-40 sq ft

Once I know the size, I can show you everything you'll need for professional installation!"""
            
            # Calculate materials for project
            room_size = project_details.get('size', 50)
            room_type = project_details.get('room_type', 'bathroom')
            
            materials = self.calculate_material_needs(subway_tiles[0], room_size, room_type)
            
            # Generate upselling response
            return self.generate_upselling_response(subway_tiles, project_details, materials)
            
        except Exception as e:
            logger.error(f"Error in subway upselling: {e}")
            return self._handle_search_query(query)
    
    def _format_tile_results(self, tiles: List[Dict]) -> str:
        """Format tile results for display"""
        result_parts = []
        
        for i, tile in enumerate(tiles, 1):
            price_info = f"${tile.get('price_per_sqft', 0):.2f}/sq ft"
            if tile.get('price_per_box'):
                price_info += f" (${tile['price_per_box']:.2f}/box)"
            
            result_parts.append(
                f"{i}. **{tile['title']}** - {price_info}\n"
                f"   SKU: {tile['sku']} | {tile.get('size_shape', 'Standard size')}"
            )
        
        return "\n".join(result_parts)
    
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
            
            # Handle price information from different sources
            if result.get('price_estimate'):
                price_info = f" - ${result['price_estimate']:.2f}"
            elif result.get('price_per_piece'):
                price_info = f" - ${result['price_per_piece']:.2f}/each"
            elif result.get('price_per_box'):
                price_info = f" - ${result['price_per_box']:.2f}/box"
            elif result.get('price_per_sqft'):
                price_info = f" - ${result['price_per_sqft']:.2f}/sq ft"
            
            # Handle size information
            size_str = f" - {result['size_shape']}" if result.get('size_shape') else ""
            
            # Handle content description (truncate if too long)
            content_preview = ""
            if result.get('content'):
                content = result['content']
                if len(content) > 200:
                    content_preview = f"   {content[:200]}...\n"
                else:
                    content_preview = f"   {content}\n"
            
            # Handle similarity score or relevance
            score_info = ""
            if result.get('similarity_score'):
                score_info = f" (Match: {result['similarity_score']:.2f})"
            elif result.get('relevance_score'):
                score_info = f" (Relevance: {result['relevance_score']:.2f})"
            
            response_parts.append(
                f"{i}. **{result['title']}** (SKU: {result['sku']}){score_info}\n"
                f"   {price_info}{size_str}\n"
                f"{content_preview}"
                f"   More details: https://www.tileshop.com/product/{result['sku']}\n"
            )
        
        return "\n".join(response_parts)
    
    def _get_all_products_for_analysis(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all products for analytical queries"""
        try:
            # Get products with essential fields for analysis from product_embeddings table
            analysis_sql = f"""
                COPY (
                    SELECT 
                        sku, 
                        title, 
                        content,
                        -- Extract price information from content
                        CASE 
                            WHEN content ~ '\\$[0-9]+\\.[0-9]+' THEN 
                                (regexp_matches(content, '\\$([0-9]+\\.[0-9]+)', 'g'))[1]::decimal
                            ELSE NULL
                        END as price_estimate,
                        -- Extract size information
                        CASE 
                            WHEN content ~ '[0-9]+ x [0-9]+ in\\.' THEN 
                                (regexp_matches(content, '([0-9]+ x [0-9]+ in\\.)', 'g'))[1]
                            ELSE NULL
                        END as size_shape
                    FROM product_embeddings
                    WHERE content IS NOT NULL 
                    ORDER BY sku
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
                    row['price_estimate'] = float(row['price_estimate']) if row['price_estimate'] else None
                except:
                    row['price_estimate'] = None
                    
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
        
        # Handle special cases first
        if 'slip' in query and ('resistant' in query or 'resist' in query):
            # For slip-resistant queries, search for textured surfaces and matte finishes
            return 'textured matte honed'
        
        if 'dcof' in query:
            # DCOF is a specific tile rating - if not found, suggest alternative
            return 'dcof coefficient friction slip resistant textured'
        
        if 'lft' in query:
            # LFT is a specific product line - search for LFT products (mortar/thinset)
            return 'lft'
        
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
        
        # Otherwise, remove common words and numbers (but keep important words like 'under', 'best', etc.)
        stop_words = ['find', 'show', 'me', 'get', 'the', 'a', 'an', 'some', 'any', 'list', 'suggest', 'what', 'can', 'you', 'tell', 'about', 'your']
        words = query.split()
        meaningful_words = [w for w in words if w not in stop_words and not w.isdigit()]
        
        return ' '.join(meaningful_words) if meaningful_words else query
    
    def sync_data(self) -> bool:
        """Sync data - not needed since we use the DatabaseSyncManager"""
        # This method is called by the RAG manager but we use the separate sync manager
        # So just return True to indicate sync is handled elsewhere
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to vector database"""
        try:
            result = subprocess.run([
                'docker', 'exec', self.supabase_container,
                'psql', '-U', 'postgres', '-d', self.db_name,
                '-c', 'SELECT COUNT(*) FROM product_embeddings;'
            ], capture_output=True, text=True, check=True)
            
            # Parse count
            count_lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip().isdigit()]
            count = int(count_lines[0]) if count_lines else 0
            
            return {
                'connected': True,
                'product_count': count,
                'message': f'Connected to vector database with {count} products'
            }
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                'connected': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }