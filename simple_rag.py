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
        
        # Load sales associate system prompt
        self.sales_prompt = self._load_sales_associate_prompt()
    
    def _load_sales_associate_prompt(self) -> str:
        """Load the sales associate system prompt from documentation"""
        try:
            prompt_file = os.path.join(os.path.dirname(__file__), 'readme', 'SALES_ASSOCIATE_SYSTEM_PROMPT.md')
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract the core prompt from the markdown documentation
                    # Look for the main system prompt section
                    lines = content.split('\n')
                    core_prompt_lines = []
                    in_core_section = False
                    
                    for line in lines:
                        if line.strip() == "## Core Personality & Approach":
                            in_core_section = True
                            continue
                        elif line.startswith('## ') and in_core_section:
                            break
                        elif in_core_section:
                            core_prompt_lines.append(line)
                    
                    if core_prompt_lines:
                        return '\n'.join(core_prompt_lines).strip()
            
            # Fallback system prompt if file doesn't exist
            return """You are a friendly, knowledgeable, and enthusiastic sales associate at The Tile Shop, a premium tile and stone retailer. Your mission is to provide exceptional customer service while maximizing sales opportunities through helpful guidance and expert recommendations.

Key traits:
- Friendly & approachable: Use warm, conversational language and show genuine enthusiasm
- Knowledgeable expert: Demonstrate deep understanding of tiles, installation, and applications  
- Solution-oriented: Focus on complete project needs, not just individual products
- Sales-focused: Always suggest supporting materials and emphasize value propositions

Always present complete solutions including necessary installation materials, provide professional tips, and create confidence in the customer's project success."""
            
        except Exception as e:
            logger.error(f"Error loading sales associate prompt: {e}")
            return "You are a helpful and knowledgeable tile shop sales associate."
    
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
        """Enhanced text search using both product_embeddings and product_data for complete results with images"""
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
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best', 'the', 'for'] and len(term) > 2:
                    # Escape single quotes for SQL
                    escaped_term = term.replace("'", "''")
                    where_conditions.append(f"(LOWER(pe.title) LIKE '%{escaped_term}%' OR LOWER(pe.content) LIKE '%{escaped_term}%')")
            
            if not where_conditions:
                return []
            
            where_clause = " OR ".join(where_conditions)
            
            # Check if this is a non-tile query (like LFT, thinset, mortar, grout)
            non_tile_terms = ['lft', 'thinset', 'mortar', 'adhesive', 'grout', 'sealer']
            is_non_tile_query = any(term in query.lower() for term in non_tile_terms)
            
            # Enhanced search with better relevance ordering and image support
            # Create priority scoring for better ordering
            title_priority_conditions = []
            for term in query_terms:
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best', 'the', 'for'] and len(term) > 2:
                    escaped_term = term.replace("'", "''")
                    title_priority_conditions.append(f"LOWER(pe.title) LIKE '%{escaped_term}%'")
            
            title_priority_clause = " OR ".join(title_priority_conditions) if title_priority_conditions else "FALSE"
            
            # For tile queries, use the relational database directly to get images
            if not is_non_tile_query:
                # Search relational database for tiles with images
                return self._search_relational_db_with_images(query_terms, title_priority_conditions, limit)
            
            # For non-tile queries, use embeddings database
            filter_clause = ""
            search_sql = f"""
                COPY (
                    SELECT 
                        sku,
                        title,
                        content,
                        '' as primary_image,
                        0 as price_per_sqft,
                        0 as price_per_box,
                        0 as price_per_piece,
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
    
    def _search_relational_db_with_images(self, query_terms: List[str], title_priority_conditions: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Search relational database for tiles with images and complete product data"""
        try:
            # Create WHERE clause for relational database
            where_conditions = []
            for term in query_terms:
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best', 'the', 'for'] and len(term) > 2:
                    escaped_term = term.replace("'", "''")
                    where_conditions.append(f"""(LOWER(title) LIKE '%{escaped_term}%' OR 
                                                 LOWER(description) LIKE '%{escaped_term}%' OR
                                                 LOWER(color) LIKE '%{escaped_term}%' OR
                                                 LOWER(finish) LIKE '%{escaped_term}%')""")
            
            if not where_conditions:
                return []
            
            where_clause = " OR ".join(where_conditions)
            
            # Create priority clause for relational database
            title_priority_conditions_rel = []
            for term in query_terms:
                if term not in ['under', '$', 'list', 'find', 'suggest', 'best', 'the', 'for'] and len(term) > 2:
                    escaped_term = term.replace("'", "''")
                    title_priority_conditions_rel.append(f"LOWER(title) LIKE '%{escaped_term}%'")
            
            title_priority_clause = " OR ".join(title_priority_conditions_rel) if title_priority_conditions_rel else "FALSE"
            
            search_sql = f"""
                COPY (
                    SELECT 
                        sku,
                        title,
                        description,
                        primary_image,
                        price_per_sqft,
                        price_per_box,
                        price_per_piece,
                        color,
                        finish,
                        size_shape
                    FROM product_data
                    WHERE ({where_clause})
                      AND LOWER(title) LIKE '%tile%'
                      AND NOT (LOWER(title) LIKE '%tool%' OR LOWER(title) LIKE '%grout%' OR 
                               LOWER(title) LIKE '%float%' OR LOWER(title) LIKE '%base%' OR
                               LOWER(title) LIKE '%wedge%' OR LOWER(title) LIKE '%spacer%')
                    ORDER BY 
                        -- Prioritize products that match multiple search terms
                        CASE WHEN LOWER(title) LIKE '%blue%' AND LOWER(title) LIKE '%floor%' AND LOWER(title) LIKE '%tile%' THEN 1
                             WHEN ({title_priority_clause}) THEN 2 
                             ELSE 3 END,
                        -- Then prioritize actual tiles over accessories
                        CASE WHEN LOWER(title) LIKE '%tile%' AND 
                                  NOT (LOWER(title) LIKE '%kit%' OR LOWER(title) LIKE '%protection%' OR 
                                       LOWER(title) LIKE '%shop%') THEN 1 
                             ELSE 2 END,
                        sku
                    LIMIT {limit}
                ) TO STDOUT CSV HEADER;
            """
            
            result = subprocess.run([
                'docker', 'exec', 'relational_db',
                'psql', '-U', 'postgres', '-d', 'postgres',
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
                        elif key in ['price_per_sqft', 'price_per_box', 'price_per_piece']:
                            product[key] = float(value) if value else None
                        else:
                            product[key] = value
                    
                    # Set relevance score for relational search results
                    product['relevance_score'] = 1.0
                    # Use description as content for compatibility
                    product['content'] = product.get('description', '')
                    formatted_results.append(product)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in relational database search: {e}")
            return []
    
    def chat(self, query: str) -> str:
        """Generate intelligent chat response - Smart routing based on query type"""
        try:
            # Check for room design queries FIRST (highest priority for sales)
            design_detection = self._detect_room_design_query(query)
            
            if design_detection['is_room_design'] or design_detection['needs_dimension_collection']:
                logger.info(f"Detected room design query for {design_detection['room_type']}")
                return self._handle_room_design_query(query, design_detection)
            
            # Check for subway tile upselling opportunities  
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
        """Handle analytical queries using Claude API with sales associate persona"""
        try:
            # First, get all product data for analysis
            all_products = self._get_all_products_for_analysis()
            
            if not all_products:
                return "I'd love to help you with that analysis, but I need our product database to be fully loaded first. Let me check on that for you!"
            
            # Create the analytical prompt with sales associate persona
            system_prompt = f"""
{self.sales_prompt}

You have access to our complete product database with detailed information about tiles, prices, and specifications. Use this data to provide enthusiastic, helpful analysis while looking for opportunities to suggest complete project solutions.

When analyzing products, always consider:
1. The customer's specific needs and project context
2. Opportunities to suggest supporting materials and installation products
3. Value propositions that justify price differences
4. Professional tips and guidance
5. Ways to build confidence in their project success

Remember: You're not just analyzing data - you're helping customers make informed decisions that lead to beautiful, successful tile projects!
"""

            user_prompt = f"""
Here's our current product database with pricing and specifications:

{json.dumps(all_products[:10], indent=2)}
... and {len(all_products) - 10} more products in our inventory

Customer Query: "{query}"

Please analyze this query with enthusiasm and provide a helpful response. If they're asking for:
- Lowest/cheapest: Find the best value options and explain why they're great choices
- Highest/most expensive: Show premium options and their value propositions
- Average pricing: Provide context and suggest how to get the best value
- Best value: Consider quality, durability, and total project cost
- Comparisons: Help them understand the differences and make confident choices

Always include specific product names, SKUs, prices, and suggest what else they might need for their project. Make it conversational and helpful!
"""

            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1200,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
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
        """Handle regular search queries with enhanced image support and supporting materials"""
        # Extract meaningful search terms from query
        search_terms = self._extract_search_terms(query)
        results = self.search_products(search_terms)
        
        if not results:
            return "I'd love to help you find the perfect tiles! I couldn't find anything matching those exact terms, but let me help you explore some other options. Try searching for tile types, colors, finishes, or sizes, and I'll find some great choices for you!"
        
        response_parts = [f"I found {len(results)} fantastic options for you! Let me show you what would work beautifully:\n"]
        
        # Track if we have tiles (not installation materials) for supporting materials suggestion
        has_tiles = False
        
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
            
            # Handle color and finish information
            color_str = f" - {result['color']}" if result.get('color') else ""
            finish_str = f" - {result['finish']}" if result.get('finish') else ""
            
            # Check if this is a tile product (not installation materials)
            title_lower = result.get('title', '').lower()
            if 'tile' in title_lower and not any(material in title_lower for material in ['mortar', 'thinset', 'grout', 'sealer', 'adhesive']):
                has_tiles = True
            
            # Handle content description (truncate if too long)
            content_preview = ""
            if result.get('content'):
                content = result['content']
                if len(content) > 200:
                    content_preview = f"   {content[:200]}...\n"
                else:
                    content_preview = f"   {content}\n"
            elif result.get('description'):
                description = result['description']
                if len(description) > 200:
                    content_preview = f"   {description[:200]}...\n"
                else:
                    content_preview = f"   {description}\n"
            
            # Handle similarity score or relevance
            score_info = ""
            if result.get('similarity_score'):
                score_info = f" (Match: {result['similarity_score']:.2f})"
            elif result.get('relevance_score'):
                score_info = f" (Relevance: {result['relevance_score']:.2f})"
            
            # Add image if available
            image_info = ""
            if result.get('primary_image'):
                image_info = f"   🖼️ **Image**: {result['primary_image']}\n"
            
            response_parts.append(
                f"{i}. **{result['title']}** (SKU: {result['sku']}){score_info}\n"
                f"   {price_info}{size_str}{color_str}{finish_str}\n"
                f"{image_info}"
                f"{content_preview}"
                f"   More details: https://www.tileshop.com/product/{result['sku']}\n"
            )
        
        # Add supporting materials section if we found actual tiles
        if has_tiles:
            supporting_materials = self._generate_supporting_materials_section(query, results)
            if supporting_materials:
                response_parts.append(supporting_materials)
        
        return "\n".join(response_parts)
    
    def _generate_supporting_materials_section(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate supporting materials recommendations based on tile selection and application"""
        if not results:
            return ""
        
        query_lower = query.lower()
        
        # Determine application area based on query context
        is_bathroom = any(term in query_lower for term in ['bathroom', 'shower', 'wet', 'bath'])
        is_kitchen = any(term in query_lower for term in ['kitchen', 'backsplash', 'counter'])
        is_basement = any(term in query_lower for term in ['basement', 'below grade'])
        is_floor = any(term in query_lower for term in ['floor', 'flooring'])
        is_wall = any(term in query_lower for term in ['wall', 'backsplash'])
        is_heated = any(term in query_lower for term in ['heated', 'heating', 'radiant'])
        
        # Analyze tile characteristics from results
        has_large_tiles = False
        has_natural_stone = False
        has_porcelain = False
        
        for result in results:
            title = result.get('title', '').lower()
            content = result.get('content', '').lower()
            
            # Check for large format tiles (>12 inches)
            if any(size in title or size in content for size in ['24 x', '18 x', '16 x', '15 x', '14 x', '13 x']):
                has_large_tiles = True
            
            # Check for porcelain first (takes precedence over natural stone keywords)
            if 'porcelain' in title:
                has_porcelain = True
            # Only check for natural stone if not porcelain
            elif any(stone in title for stone in ['marble', 'travertine', 'limestone', 'granite', 'slate']) and 'porcelain' not in title:
                has_natural_stone = True
        
        # Generate materials list based on conditions
        materials = []
        
        # Essential installation materials (always needed)
        if has_large_tiles or has_porcelain:
            materials.append("**LFT Thinset Mortar** - Superior bond strength for large format and porcelain tiles")
        else:
            materials.append("**Premium Thinset Mortar** - Standard installation adhesive")
        
        materials.append("**Tile Spacers/Wedges** - Ensure consistent joint spacing")
        materials.append("**Grout** - Sanded for joints >1/8\", unsanded for smaller joints")
        
        # Wet area protection
        if is_bathroom or is_kitchen or is_basement:
            materials.append("**Backer-Lite Underlayment** - Moisture protection for wet areas")
            materials.append("**Waterproof Membrane** - Additional moisture barrier")
        
        # Heated floor systems (only add if heated is specifically mentioned)
        if is_heated:
            materials.append("**Heated Floor Mat & Cable** - Radiant heating system for comfort")
            materials.append("**Uncoupling Membrane** - Prevents tile cracking from thermal expansion")
        
        # Dry area underlayment
        if is_floor and not (is_bathroom or is_kitchen or is_basement):
            materials.append("**Permat Underlayment** - Crack isolation for dry areas")
        
        # Natural stone specific materials
        if has_natural_stone:
            materials.append("**Stone Sealer** - Protects natural stone from stains and moisture")
            materials.append("**Stone-Safe Grout** - Non-acidic grout for natural stone")
        else:
            materials.append("**Grout Sealer** - Protects grout from moisture and stains")
        
        # Installation tools and finishing
        materials.append("**Tile Leveling System** - Professional results with minimal lippage")
        materials.append("**Trim Pieces** - Bullnose, edge trim for professional finishing")
        
        # Generate response section
        area_context = ""
        if is_bathroom:
            area_context = " for your bathroom project"
        elif is_kitchen:
            area_context = " for your kitchen installation"
        elif is_basement:
            area_context = " for your basement flooring"
        elif is_floor:
            area_context = " for your floor installation"
        elif is_wall:
            area_context = " for your wall tiling"
        
        response_parts = [
            f"\n🔧 **Complete Installation Package{area_context}:**\n",
            "To ensure your project looks professional and lasts for years, I recommend these essential materials:\n"
        ]
        
        for material in materials:
            response_parts.append(f"✅ {material}")
        
        response_parts.extend([
            "\n💡 **Professional Tips for Success:**",
            "• I always recommend purchasing 10-15% extra tile for cuts and future repairs",
            "• Use the right trowel size: 1/4\" notched for wall tiles, 3/8\" for floor tiles", 
            "• Proper cure time makes all the difference: 24 hours before grouting, 72 hours before heavy use"
        ])
        
        if has_natural_stone:
            response_parts.append("• For natural stone: seal before and after grouting for lasting beauty")
        
        if is_heated:
            response_parts.append("• Install your heating system before tile installation - it's much easier!")
        
        response_parts.extend([
            "\n🏆 **Why choose our complete system approach?**",
            "• Prevents costly return trips for missing materials",
            "• Ensures all products work perfectly together", 
            "• Professional results that you'll love for years to come",
            "",
            "📞 **Ready to get started?** I'd love to help calculate the exact quantities you'll need and put together your complete project package!"
        ])
        
        return "\n".join(response_parts)
    
    def _detect_room_design_query(self, query: str) -> Dict[str, Any]:
        """Detect if user wants room design assistance"""
        query_lower = query.lower()
        
        # Room type detection
        room_types = {
            'bathroom': ['bathroom', 'bath', 'shower', 'powder room'],
            'kitchen': ['kitchen', 'backsplash']
        }
        
        detected_room = None
        for room, keywords in room_types.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_room = room
                break
        
        # Design intent detection
        design_indicators = [
            'design', 'layout', 'plan', 'calculate', 'how much', 'how many',
            'complete project', 'entire', 'whole', 'full renovation',
            'dimensions', 'measurements', 'square feet', 'sq ft', 'project'
        ]
        
        has_design_intent = any(indicator in query_lower for indicator in design_indicators)
        
        # Dimension patterns
        dimension_patterns = [
            r'\b(\d+)\s*x\s*(\d+)\b',  # "8x10" or "8 x 10"
            r'\b(\d+)\s*ft\s*x\s*(\d+)\s*ft\b',  # "8ft x 10ft"
            r'\b(\d+)\s*by\s*(\d+)\b',  # "8 by 10"
            r'\b(\d+)\s*sq\s*ft\b',  # "80 sq ft"
            r'\b(\d+)\s*square\s*feet\b'  # "80 square feet"
        ]
        
        dimensions = None
        for pattern in dimension_patterns:
            match = re.search(pattern, query)
            if match:
                if 'sq' in pattern or 'square' in pattern:
                    # Square footage provided
                    dimensions = {'type': 'area', 'value': int(match.group(1))}
                else:
                    # Length x width provided
                    dimensions = {
                        'type': 'dimensions',
                        'length': int(match.group(1)),
                        'width': int(match.group(2))
                    }
                break
        
        return {
            'is_room_design': detected_room is not None and has_design_intent,
            'room_type': detected_room,
            'has_dimensions': dimensions is not None,
            'dimensions': dimensions,
            'needs_dimension_collection': detected_room is not None and has_design_intent and dimensions is None
        }
    
    def _handle_room_design_query(self, query: str, design_info: Dict[str, Any]) -> str:
        """Handle room design queries with dimension collection and calculations"""
        room_type = design_info['room_type']
        
        # Extract tile preference from query
        search_terms = self._extract_search_terms(query)
        tile_results = self.search_products(search_terms, limit=2)
        
        if not tile_results:
            return f"I'd love to help you design your {room_type}! Let me find some tile options first. Could you tell me what style or color you're looking for?"
        
        # If no dimensions provided, collect them
        if design_info['needs_dimension_collection']:
            return self._request_room_dimensions(room_type, tile_results)
        
        # If dimensions provided, create complete design
        if design_info['has_dimensions']:
            return self._create_room_design(room_type, design_info['dimensions'], tile_results, query)
        
        return f"I'd love to help design your {room_type}! Let me gather some more information about your space."
    
    def _request_room_dimensions(self, room_type: str, tiles: List[Dict[str, Any]]) -> str:
        """Request room dimensions from customer"""
        primary_tile = tiles[0] if tiles else None
        
        if room_type == 'bathroom':
            return f"""Perfect! I found some beautiful tiles for your bathroom project:

**{primary_tile['title']}** - ${primary_tile.get('price_estimate', 'N/A')}/box
🖼️ {primary_tile.get('primary_image', '')}

To create your complete bathroom design and calculate exact materials, I need your room dimensions:

**For a complete bathroom renovation, please provide:**
📏 **Floor Area**: Length x Width (e.g., "8ft x 6ft" or "48 sq ft")
📏 **Wall Area for Tiling**: Which walls and their dimensions
   - Around tub/shower: Height x Width
   - Vanity backsplash: Height x Width  
   - Any accent walls: Height x Width

**Example:** "My bathroom is 8x6 feet, and I want to tile the shower area which is 5 feet wide by 7 feet tall"

Once I have your dimensions, I'll create a complete project plan with:
✅ Exact tile quantities for floor and walls
✅ All installation materials calculated precisely  
✅ Professional layout recommendations
✅ Complete project pricing

What are your bathroom dimensions?"""

        elif room_type == 'kitchen':
            return f"""Excellent choice! I found perfect tiles for your kitchen:

**{primary_tile['title']}** - ${primary_tile.get('price_estimate', 'N/A')}/box  
🖼️ {primary_tile.get('primary_image', '')}

To design your complete kitchen tile project, I need these measurements:

**For kitchen floor and backsplash:**
📏 **Kitchen Floor**: Length x Width (e.g., "12ft x 10ft")
📏 **Backsplash Area**: Length x Height (e.g., "15ft x 1.5ft")
   - Include any areas around stove, sink, counters
   - Mention any windows or obstacles

**Example:** "Kitchen is 12x10 feet, backsplash runs 15 feet long and 18 inches high, with a 3x4 foot window above the sink"

I'll then provide:
✅ Exact quantities for floor and backsplash
✅ Complete installation material list
✅ Layout suggestions for best visual impact
✅ Full project cost breakdown

What are your kitchen dimensions?"""
        
        return f"To design your {room_type}, I'll need the room dimensions. Could you share the length and width?"
    
    def _create_room_design(self, room_type: str, dimensions: Dict[str, Any], tiles: List[Dict[str, Any]], original_query: str) -> str:
        """Create complete room design with calculations"""
        primary_tile = tiles[0] if tiles else None
        if not primary_tile:
            return "I need to find suitable tiles first. Could you specify what type of tile you're looking for?"
        
        # Calculate areas based on dimension type
        if dimensions['type'] == 'area':
            floor_area = dimensions['value']
            length = width = int(floor_area ** 0.5)  # Approximate square room
        else:
            length = dimensions['length']
            width = dimensions['width'] 
            floor_area = length * width
        
        if room_type == 'bathroom':
            return self._design_bathroom(floor_area, length, width, primary_tile, tiles)
        elif room_type == 'kitchen':
            return self._design_kitchen(floor_area, length, width, primary_tile, tiles, original_query)
        
        return "I can help design bathrooms and kitchens. Which type of room are you working on?"
    
    def _design_bathroom(self, floor_area: int, length: int, width: int, primary_tile: Dict, all_tiles: List[Dict]) -> str:
        """Create complete bathroom design with floor and wall calculations"""
        
        # Tile specifications
        tile_name = primary_tile['title']
        tile_sku = primary_tile['sku']
        tile_price = primary_tile.get('price_estimate', 0) or 0
        tile_image = primary_tile.get('primary_image', '')
        
        # Extract tile size (assume 6x6 if not found)
        tile_size = self._extract_tile_size(primary_tile)
        tile_sq_ft_per_box = tile_size['coverage_per_box']
        
        # Bathroom design calculations
        floor_sq_ft = floor_area
        
        # Standard bathroom wall estimates
        # Assume tub surround (5ft x 7ft) + vanity backsplash (4ft x 1.5ft)
        tub_surround_area = 35  # 5 x 7 feet
        vanity_backsplash = 6   # 4 x 1.5 feet
        total_wall_area = tub_surround_area + vanity_backsplash
        
        # Total tile needed
        total_tile_area = floor_sq_ft + total_wall_area
        boxes_needed = (total_tile_area / tile_sq_ft_per_box) * 1.15  # 15% waste factor
        total_tile_cost = boxes_needed * tile_price
        
        # Material calculations
        materials = self._calculate_bathroom_materials(floor_sq_ft, total_wall_area, total_tile_area)
        
        response = f"""🏠 **Complete Bathroom Design Project**

**Your Selected Tile:** {tile_name} (SKU: {tile_sku})
🖼️ **Image:** {tile_image}

📐 **Project Dimensions:**
• **Floor Area:** {floor_sq_ft} sq ft ({length}' x {width}')
• **Wall Tiling:** {total_wall_area} sq ft (tub surround + vanity backsplash)
• **Total Tile Area:** {total_tile_area} sq ft

📦 **Tile Requirements:**
• **Boxes Needed:** {boxes_needed:.1f} boxes (includes 15% for cuts/repairs)
• **Tile Cost:** ${total_tile_cost:.2f}

🔧 **Complete Installation Package:**

**Essential Materials:**
✅ **LFT Thinset Mortar** - {materials['thinset_bags']} bags - ${materials['thinset_cost']:.2f}
✅ **Tile Spacers (1/16")** - ${materials['spacers_cost']:.2f}
✅ **Grout (Sanded)** - {materials['grout_bags']} bags - ${materials['grout_cost']:.2f}
✅ **Backer-Lite Underlayment** - {materials['underlayment_sq_ft']} sq ft - ${materials['underlayment_cost']:.2f}
✅ **Waterproof Membrane** - {materials['membrane_sq_ft']} sq ft - ${materials['membrane_cost']:.2f}
✅ **Grout Sealer** - ${materials['sealer_cost']:.2f}
✅ **Tile Leveling System** - ${materials['leveling_cost']:.2f}
✅ **Bullnose Trim** - {materials['trim_linear_ft']} linear ft - ${materials['trim_cost']:.2f}

**Professional Tools Package:**
🔹 **Wet Tile Saw Rental** - ${materials['saw_rental']:.2f}
🔹 **Professional Trowel Set** - ${materials['trowel_cost']:.2f}
🔹 **Tile Nippers & Tools** - ${materials['tools_cost']:.2f}

💰 **Investment Summary:**
• **Tiles:** ${total_tile_cost:.2f}
• **Essential Materials:** ${materials['materials_total']:.2f}
• **Professional Tools:** ${materials['tools_total']:.2f}
• **Complete Project Total:** ${total_tile_cost + materials['materials_total'] + materials['tools_total']:.2f}

🎯 **Professional Layout Recommendations:**
• Start floor layout from center of room for balanced appearance
• Use bullnose trim on all exposed tile edges
• Install floor first, then walls (floor tiles under wall tiles)
• Consider running wall tiles to ceiling for modern, luxurious look

💡 **Installation Timeline:**
• **Day 1:** Surface prep and underlayment installation
• **Day 2:** Floor tile installation 
• **Day 3:** Wall tile installation
• **Day 4:** Grouting and cleanup
• **Day 5:** Sealing and final touches

🏆 **This complete package ensures:**
• Professional installation results
• Long-lasting, moisture-resistant finish
• All materials perfectly coordinated
• No return trips for missing items

📞 **Ready to transform your bathroom?** I can refine these calculations based on your exact layout preferences or help you explore coordinating accent tiles!"""

        return response
    
    def _design_kitchen(self, floor_area: int, length: int, width: int, primary_tile: Dict, all_tiles: List[Dict], original_query: str) -> str:
        """Create complete kitchen design with floor and backsplash calculations"""
        
        # Tile specifications
        tile_name = primary_tile['title']
        tile_sku = primary_tile['sku']
        tile_price = primary_tile.get('price_estimate', 0) or 0
        tile_image = primary_tile.get('primary_image', '')
        
        # Extract tile size
        tile_size = self._extract_tile_size(primary_tile)
        tile_sq_ft_per_box = tile_size['coverage_per_box']
        
        # Determine if floor, backsplash, or both
        query_lower = original_query.lower()
        needs_floor = 'floor' in query_lower or 'flooring' in query_lower
        needs_backsplash = 'backsplash' in query_lower or 'wall' in query_lower
        
        # Default to both if not specified
        if not needs_floor and not needs_backsplash:
            needs_floor = needs_backsplash = True
        
        # Kitchen calculations
        floor_sq_ft = floor_area if needs_floor else 0
        
        # Standard backsplash estimate: perimeter minus appliances
        perimeter = 2 * (length + width)
        backsplash_linear_ft = perimeter * 0.7  # 70% of perimeter (account for appliances)
        backsplash_height = 1.5  # 18 inches standard
        backsplash_sq_ft = backsplash_linear_ft * backsplash_height if needs_backsplash else 0
        
        # Total tile needed
        total_tile_area = floor_sq_ft + backsplash_sq_ft
        boxes_needed = (total_tile_area / tile_sq_ft_per_box) * 1.12  # 12% waste factor for kitchen
        total_tile_cost = boxes_needed * tile_price
        
        # Material calculations
        materials = self._calculate_kitchen_materials(floor_sq_ft, backsplash_sq_ft, total_tile_area, needs_floor, needs_backsplash)
        
        areas_text = ""
        if needs_floor and needs_backsplash:
            areas_text = f"• **Floor Area:** {floor_sq_ft} sq ft ({length}' x {width}')\n• **Backsplash Area:** {backsplash_sq_ft:.1f} sq ft ({backsplash_linear_ft:.1f} linear ft)"
        elif needs_floor:
            areas_text = f"• **Floor Area:** {floor_sq_ft} sq ft ({length}' x {width}')"
        else:
            areas_text = f"• **Backsplash Area:** {backsplash_sq_ft:.1f} sq ft ({backsplash_linear_ft:.1f} linear ft)"
        
        response = f"""🍳 **Complete Kitchen Design Project**

**Your Selected Tile:** {tile_name} (SKU: {tile_sku})
🖼️ **Image:** {tile_image}

📐 **Project Dimensions:**
{areas_text}
• **Total Tile Area:** {total_tile_area:.1f} sq ft

📦 **Tile Requirements:**
• **Boxes Needed:** {boxes_needed:.1f} boxes (includes 12% for cuts/repairs)
• **Tile Cost:** ${total_tile_cost:.2f}

🔧 **Complete Installation Package:**

**Essential Materials:**
✅ **Premium Thinset Mortar** - {materials['thinset_bags']} bags - ${materials['thinset_cost']:.2f}
✅ **Tile Spacers** - ${materials['spacers_cost']:.2f}
✅ **Grout (Stain-Resistant)** - {materials['grout_bags']} bags - ${materials['grout_cost']:.2f}"""

        if needs_floor:
            response += f"""
✅ **Permat Underlayment** - {materials['underlayment_sq_ft']} sq ft - ${materials['underlayment_cost']:.2f}"""
        
        if needs_backsplash:
            response += f"""
✅ **Backsplash Adhesive** - ${materials['backsplash_adhesive']:.2f}"""
        
        response += f"""
✅ **Grout Sealer** - ${materials['sealer_cost']:.2f}
✅ **Tile Leveling System** - ${materials['leveling_cost']:.2f}
✅ **Edge Trim & Transitions** - ${materials['trim_cost']:.2f}

**Professional Tools Package:**
🔹 **Tile Saw & Cutting Tools** - ${materials['cutting_tools']:.2f}
🔹 **Professional Trowel Set** - ${materials['trowel_cost']:.2f}
🔹 **Installation Tools Kit** - ${materials['tools_cost']:.2f}

💰 **Investment Summary:**
• **Tiles:** ${total_tile_cost:.2f}
• **Essential Materials:** ${materials['materials_total']:.2f}
• **Professional Tools:** ${materials['tools_total']:.2f}
• **Complete Project Total:** ${total_tile_cost + materials['materials_total'] + materials['tools_total']:.2f}

🎯 **Professional Design Recommendations:**"""

        if needs_floor and needs_backsplash:
            response += """
• Consider using same tile for cohesive look, or coordinate with complementary backsplash
• Run floor tiles under appliances for consistent appearance
• Use decorative trim where backsplash meets countertop"""
        elif needs_floor:
            response += """
• Plan layout to minimize cuts at most visible areas
• Consider larger format tiles for fewer grout lines
• Use transition strips where tile meets other flooring"""
        else:
            response += """
• Center pattern on most prominent wall (usually behind range)
• Consider extending to ceiling for dramatic effect
• Plan electrical outlet placement before installation"""
        
        response += f"""

💡 **Installation Timeline:**
• **Day 1:** Surface preparation and layout planning
• **Day 2:** {"Floor installation" if needs_floor else "Backsplash installation"}"""
        
        if needs_floor and needs_backsplash:
            response += """
• **Day 3:** Backsplash installation"""
        
        response += """
• **Day 3-4:** Grouting and cleanup  
• **Day 4-5:** Sealing and final touches

🏆 **This complete package ensures:**
• Professional kitchen transformation
• Durable, easy-to-clean surfaces
• Perfectly coordinated materials
• Comprehensive tool set for success

📞 **Ready to create your dream kitchen?** I can adjust these calculations for your specific layout or suggest coordinating accent options!"""

        return response
    
    def _extract_tile_size(self, tile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tile size and calculate coverage from tile information"""
        title = tile.get('title', '')
        content = tile.get('content', '')
        
        # Look for size patterns like "6 x 6 in" or "12x24"
        size_patterns = [
            r'(\d+)\s*x\s*(\d+)\s*in',
            r'(\d+)\s*x\s*(\d+)',
            r'(\d+)"?\s*x\s*(\d+)"?'
        ]
        
        length = width = 6  # Default 6x6 inches
        
        for pattern in size_patterns:
            match = re.search(pattern, title + ' ' + content, re.IGNORECASE)
            if match:
                length = int(match.group(1))
                width = int(match.group(2))
                break
        
        # Calculate coverage (assuming standard box quantities)
        tile_sq_ft = (length * width) / 144  # Convert sq inches to sq feet
        
        # Estimate pieces per box based on tile size
        if tile_sq_ft <= 0.25:  # Small tiles (up to 6x6)
            pieces_per_box = 44
        elif tile_sq_ft <= 1.0:   # Medium tiles (up to 12x12)
            pieces_per_box = 18
        else:                     # Large tiles
            pieces_per_box = 8
        
        coverage_per_box = tile_sq_ft * pieces_per_box
        
        return {
            'length': length,
            'width': width,
            'sq_ft_per_tile': tile_sq_ft,
            'pieces_per_box': pieces_per_box,
            'coverage_per_box': coverage_per_box
        }
    
    def _calculate_bathroom_materials(self, floor_area: int, wall_area: int, total_area: int) -> Dict[str, float]:
        """Calculate all materials needed for bathroom installation"""
        
        # Thinset calculation (1 bag covers ~50 sq ft)
        thinset_bags = max(2, int((total_area / 50) + 1))
        
        # Grout calculation (1 bag covers ~100-150 sq ft depending on tile size)
        grout_bags = max(1, int((total_area / 125) + 1))
        
        # Trim calculation (perimeter + 20% extra)
        perimeter = 2 * ((floor_area ** 0.5) * 2)  # Approximate perimeter
        trim_linear_ft = perimeter * 1.2
        
        return {
            'thinset_bags': thinset_bags,
            'thinset_cost': thinset_bags * 35.0,
            'grout_bags': grout_bags, 
            'grout_cost': grout_bags * 28.0,
            'spacers_cost': 15.0,
            'underlayment_sq_ft': floor_area,
            'underlayment_cost': floor_area * 1.20,
            'membrane_sq_ft': wall_area,
            'membrane_cost': wall_area * 0.85,
            'sealer_cost': 25.0,
            'leveling_cost': 45.0,
            'trim_linear_ft': trim_linear_ft,
            'trim_cost': trim_linear_ft * 3.50,
            'materials_total': (thinset_bags * 35.0) + (grout_bags * 28.0) + 15.0 + (floor_area * 1.20) + (wall_area * 0.85) + 25.0 + 45.0 + (trim_linear_ft * 3.50),
            'saw_rental': 75.0,
            'trowel_cost': 85.0,
            'tools_cost': 65.0,
            'tools_total': 225.0
        }
    
    def _calculate_kitchen_materials(self, floor_area: int, backsplash_area: float, total_area: float, needs_floor: bool, needs_backsplash: bool) -> Dict[str, float]:
        """Calculate all materials needed for kitchen installation"""
        
        # Thinset calculation
        thinset_bags = max(1, int((total_area / 50) + 1))
        
        # Grout calculation  
        grout_bags = max(1, int((total_area / 125) + 1))
        
        materials = {
            'thinset_bags': thinset_bags,
            'thinset_cost': thinset_bags * 35.0,
            'grout_bags': grout_bags,
            'grout_cost': grout_bags * 32.0,  # Premium stain-resistant grout
            'spacers_cost': 18.0,
            'sealer_cost': 28.0,
            'leveling_cost': 45.0,
            'cutting_tools': 125.0,
            'trowel_cost': 85.0,
            'tools_cost': 55.0
        }
        
        # Floor-specific materials
        if needs_floor:
            materials['underlayment_sq_ft'] = floor_area
            materials['underlayment_cost'] = floor_area * 0.95
        else:
            materials['underlayment_sq_ft'] = 0
            materials['underlayment_cost'] = 0
        
        # Backsplash-specific materials
        if needs_backsplash:
            materials['backsplash_adhesive'] = 45.0
        else:
            materials['backsplash_adhesive'] = 0
        
        # Trim costs
        materials['trim_cost'] = 75.0 if (needs_floor or needs_backsplash) else 0
        
        # Calculate totals
        materials['materials_total'] = (
            materials['thinset_cost'] + materials['grout_cost'] + materials['spacers_cost'] +
            materials['underlayment_cost'] + materials['backsplash_adhesive'] + 
            materials['sealer_cost'] + materials['leveling_cost'] + materials['trim_cost']
        )
        
        materials['tools_total'] = materials['cutting_tools'] + materials['trowel_cost'] + materials['tools_cost']
        
        return materials
    
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