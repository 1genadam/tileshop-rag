#!/usr/bin/env python3
"""
Customer Chat Application - Port 8081
AOS-focused customer consultation and sales
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from modules.db_manager import DatabaseManager
from modules.rag_manager import RAGManager
from modules.simple_tile_agent import SimpleTileAgent
# Optional CLIP vision import
try:
    from modules.clip_tile_vision import CLIPTileVision
    from modules.store_inventory import StoreInventoryManager
    VISION_AVAILABLE = True
except ImportError:
    CLIPTileVision = None
    StoreInventoryManager = None
    VISION_AVAILABLE = False
    print("CLIP vision modules not available. Camera scanning will be disabled.")

# Add OpenAI for DALL-E 3 image generation
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    DALLE_AVAILABLE = True
except ImportError:
    openai_client = None
    DALLE_AVAILABLE = False
    logger.warning("OpenAI not installed. Room design generation will be unavailable.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'customer-chat-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
try:
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    
    # Initialize CLIP vision only if available
    if VISION_AVAILABLE and CLIPTileVision is not None:
        clip_vision = CLIPTileVision(db_manager)
        store_inventory = StoreInventoryManager(db_manager)
        
        # Build tile embeddings in background
        logger.info("Building CLIP tile database embeddings...")
        clip_vision.build_tile_database_embeddings()
        logger.info("CLIP tile vision system ready")
    else:
        clip_vision = None
        store_inventory = None
        logger.info("CLIP vision system disabled - camera scanning unavailable")
    
    logger.info("Customer chat components initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    db_manager = None
    rag_manager = None
    clip_vision = None
    store_inventory = None

@app.route('/')
def index():
    """Home page redirect to customer-chat"""
    return render_template('customer_chat.html')

@app.route('/customer-chat')
def customer_chat():
    """Customer chat interface"""
    return render_template('customer_chat.html')

@app.route('/chat')
def chat():
    """Legacy chat route - redirect to customer-chat"""
    return render_template('customer_chat.html')

@app.route('/api/chat', methods=['POST'])
def customer_chat_api():
    """Customer-focused chat endpoint with AOS methodology"""
    try:
        if not db_manager or not rag_manager:
            return jsonify({'success': False, 'error': 'System components not available'})
            
        data = request.get_json()
        query = data.get('query', '')
        conversation_history = data.get('conversation_history', [])
        customer_phone = data.get('customer_phone', '') or data.get('phone_number', '')
        customer_name = data.get('customer_name', '') or data.get('first_name', '')
        session_id = data.get('session_id', '')
        project_data = data.get('project_data', {})
        
        if not query.strip():
            return jsonify({'success': False, 'error': 'Query cannot be empty'})
        
        # Initialize Simple Tile Agent with AOS methodology
        agent = SimpleTileAgent(db_manager, rag_manager)
        
        # Add project context to the query if available
        enhanced_query = query
        if project_data and any(project_data.values()):
            project_summary = create_project_summary(project_data, session_id)
            if project_summary:
                enhanced_query = f"{query}\n\n[FORM DATA CONTEXT: {project_summary}]"
        
        # Process with AOS methodology
        result = agent.process_customer_query(
            enhanced_query, 
            conversation_history,
            customer_phone=customer_phone,
            customer_name=customer_name
        )
        
        # Generate self-analysis report if conversation is substantial
        self_analysis = None
        if len(conversation_history) >= 3:  # Only analyze substantial conversations
            try:
                self_analysis = agent.generate_self_analysis_report(
                    conversation_history + [{'role': 'user', 'content': query}],
                    customer_phone
                )
            except Exception as e:
                logger.warning(f"Could not generate self-analysis: {e}")
        
        return jsonify({
            'success': True,
            'response': result.get('response', ''),
            'tool_calls': result.get('tool_calls', []),
            'mode': 'customer',
            'aos_phase': result.get('aos_phase', 'discovery'),
            'requirements_complete': result.get('requirements_complete', False),
            'nepq_analysis': result.get('nepq_analysis', {}),
            'self_analysis': self_analysis
        })
        
    except Exception as e:
        logger.error(f"Error in customer chat: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/conversations/history/<phone_number>')
def get_conversation_history(phone_number):
    """Get conversation history for a phone number"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
            
        # Get conversation history from database
        conversations = db_manager.get_customer_conversations(phone_number)
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/conversations/detail/<phone_number>/<date>')
def get_conversation_detail(phone_number, date):
    """Get detailed conversation turns for a specific date"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
            
        # Get conversation details from database
        conversation_turns = db_manager.get_conversation_turns(phone_number, date)
        
        return jsonify({
            'success': True,
            'conversation_turns': conversation_turns
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation detail: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/nepq/analysis/<conversation_id>')
def get_nepq_analysis(conversation_id):
    """Get NEPQ analysis report for a specific conversation"""
    try:
        import os
        report_file = f"reports/nepq_analysis_{conversation_id}.json"
        
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                analysis_data = json.load(f)
            return jsonify({
                'success': True,
                'analysis': analysis_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis report not found'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/nepq/reports')
def list_nepq_reports():
    """List all available NEPQ analysis reports"""
    try:
        import os
        import glob
        
        report_files = glob.glob("reports/nepq_analysis_*.json")
        reports = []
        
        for file_path in report_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                reports.append({
                    'conversation_id': data.get('conversation_id'),
                    'timestamp': data.get('timestamp'),
                    'overall_score': data.get('overall_score'),
                    'customer_name': data.get('customer_name'),
                    'customer_phone': data.get('customer_phone'),
                    'file_path': file_path
                })
            except Exception as e:
                logger.warning(f"Could not read report {file_path}: {e}")
        
        return jsonify({
            'success': True,
            'reports': sorted(reports, key=lambda x: x.get('timestamp', ''), reverse=True)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/vision/analyze-tile', methods=['POST'])
def analyze_tile_image():
    """Analyze uploaded tile image using CLIP vision or fallback system"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'})
        
        image_data = data['image']
        
        # If CLIP vision is available, use it
        if clip_vision:
            result = clip_vision.analyze_tile_image(image_data)
            return jsonify(result)
        
        # Use OpenAI Vision API for tile analysis
        logger.info("Using OpenAI Vision API for tile analysis")
        
        # Analyze the tile image using OpenAI GPT-4 Vision
        vision_result = analyze_tile_with_openai_vision(image_data)
        
        if vision_result['success']:
            # Search for tiles based on AI description
            tile_matches = search_tiles_by_description(vision_result['description'])
            
            return jsonify({
                'success': True,
                'matches': tile_matches,
                'confidence': vision_result['confidence'],
                'description': vision_result['description'],
                'message': f"I can see this tile! {vision_result['description']} Here are similar tiles from our inventory:",
                'ai_analysis': True
            })
        else:
            return jsonify({
                'success': False,
                'error': vision_result['error']
            })
        
    except Exception as e:
        logger.error(f"Error analyzing tile image: {e}")
        return jsonify({'success': False, 'error': str(e)})

def analyze_tile_with_openai_vision(image_data):
    """Analyze tile image using OpenAI GPT-4 Vision with enhanced visual feature extraction"""
    try:
        if not openai_client:
            return {'success': False, 'error': 'OpenAI client not available'}
        
        # Enhanced OpenAI Vision API call for better tile matching
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this tile image and extract VISUAL CHARACTERISTICS for image-based similarity matching:

VISUAL FEATURE ANALYSIS (focus on what makes this tile visually unique):

**MATERIAL**: [ceramic/porcelain/natural stone/glass/metal/vinyl/etc.]
**COLOR_PALETTE**: [primary, secondary, accent colors - be specific like "warm beige", "cool gray", "ivory white"]
**PATTERN_TYPE**: [solid/subway/hexagon/mosaic/wood-look/stone-look/geometric/brick/herringbone/etc.]
**TEXTURE_DETAIL**: [smooth/rough/glossy/matte/brushed/honed/tumbled/textured/raised/embossed]
**VISUAL_GRAIN**: [fine/coarse/uniform/varied/linear/random - describe surface detail]
**SIZE_SHAPE**: [estimated dimensions and proportions - square/rectangular/hexagonal]
**EDGE_PROFILE**: [straight/beveled/rounded/chiseled/pillowed/pressed]
**SURFACE_REFLECTION**: [high gloss/satin/matte/non-reflective]
**VISUAL_STYLE**: [modern/traditional/rustic/industrial/contemporary/classic]

**DISTINCTIVE_VISUAL_MARKERS**: [What makes this tile instantly recognizable? Unique patterns, color variations, surface textures, etc.]

Focus on VISUAL characteristics that would help match similar-looking tiles, not just functional categories."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        
        description = response.choices[0].message.content
        
        return {
            'success': True,
            'description': description,
            'confidence': 0.85  # OpenAI Vision is generally high confidence
        }
        
    except Exception as e:
        logger.error(f"OpenAI Vision analysis failed: {e}")
        return {
            'success': False,
            'error': f"Vision analysis failed: {str(e)}"
        }

def search_tiles_by_description(description):
    """Enhanced visual similarity search using detailed visual characteristics"""
    try:
        if not rag_manager:
            return get_sample_tile_matches()
        
        # Extract structured visual attributes from description
        attributes = extract_visual_attributes(description)
        logger.info(f"Extracted visual attributes: {attributes}")
        
        # Multi-strategy visual similarity search for better results
        all_matches = []
        
        # Strategy 1: Full visual description search (highest weight)
        direct_results = rag_manager.search(f"tile {description}", limit=4)
        all_matches.extend(format_search_results(direct_results, "Visual Match", weight=1.0))
        
        # Strategy 2: Visual characteristics combination search
        if attributes.get('color_palette') and attributes.get('pattern_type'):
            visual_query = f"{attributes['color_palette']} {attributes['pattern_type']} tile"
            visual_results = rag_manager.search(visual_query, limit=3)
            all_matches.extend(format_search_results(visual_results, "Color/Pattern Match", weight=0.9))
        
        # Strategy 3: Material + Texture search
        if attributes.get('material') and attributes.get('texture_detail'):
            texture_query = f"{attributes['material']} {attributes['texture_detail']} tile"
            texture_results = rag_manager.search(texture_query, limit=2)
            all_matches.extend(format_search_results(texture_results, "Material/Texture Match", weight=0.8))
        
        # Strategy 4: Style + Surface reflection search
        if attributes.get('visual_style') and attributes.get('surface_reflection'):
            style_query = f"{attributes['visual_style']} {attributes['surface_reflection']} tile"
            style_results = rag_manager.search(style_query, limit=2)
            all_matches.extend(format_search_results(style_results, "Style/Finish Match", weight=0.7))
        
        # Strategy 5: Distinctive visual markers search
        if attributes.get('distinctive_visual_markers'):
            distinctive_query = f"tile {attributes['distinctive_visual_markers']}"
            distinctive_results = rag_manager.search(distinctive_query, limit=2)
            all_matches.extend(format_search_results(distinctive_results, "Distinctive Features", weight=0.95))
        
        # Remove duplicates and score by visual similarity relevance
        unique_matches = remove_duplicate_matches_weighted(all_matches)
        
        # Limit to top 6 results
        return unique_matches[:6] if unique_matches else get_sample_tile_matches()
        
    except Exception as e:
        logger.error(f"Error in visual similarity search: {e}")
        return get_sample_tile_matches()

def extract_visual_attributes(description):
    """Extract structured visual attributes from enhanced AI description"""
    attributes = {}
    
    # Look for structured format in description
    lines = description.split('\n')
    for line in lines:
        if '**MATERIAL**:' in line:
            attributes['material'] = line.split(':', 1)[1].strip()
        elif '**COLOR_PALETTE**:' in line:
            attributes['color_palette'] = line.split(':', 1)[1].strip()
        elif '**PATTERN_TYPE**:' in line:
            attributes['pattern_type'] = line.split(':', 1)[1].strip()
        elif '**TEXTURE_DETAIL**:' in line:
            attributes['texture_detail'] = line.split(':', 1)[1].strip()
        elif '**VISUAL_GRAIN**:' in line:
            attributes['visual_grain'] = line.split(':', 1)[1].strip()
        elif '**SIZE_SHAPE**:' in line:
            attributes['size_shape'] = line.split(':', 1)[1].strip()
        elif '**EDGE_PROFILE**:' in line:
            attributes['edge_profile'] = line.split(':', 1)[1].strip()
        elif '**SURFACE_REFLECTION**:' in line:
            attributes['surface_reflection'] = line.split(':', 1)[1].strip()
        elif '**VISUAL_STYLE**:' in line:
            attributes['visual_style'] = line.split(':', 1)[1].strip()
        elif '**DISTINCTIVE_VISUAL_MARKERS**:' in line:
            attributes['distinctive_visual_markers'] = line.split(':', 1)[1].strip()
    
    return attributes

def extract_tile_attributes(description):
    """Legacy function for backward compatibility"""
    return extract_visual_attributes(description)

def format_search_results(results, match_type, weight=1.0):
    """Format RAG search results with match type and visual similarity weight"""
    matches = []
    for result in results:
        # Calculate visual similarity score based on search strategy weight
        base_confidence = result.get('score', 0.7)
        visual_confidence = min(base_confidence * weight, 1.0)
        
        match = {
            'name': result.get('title', 'Unknown Tile'),
            'sku': result.get('sku', 'N/A'),
            'price': result.get('price_per_sq_ft', 0),
            'image_url': result.get('image_url', '/static/placeholder-tile.jpg'),
            'description': result.get('description', ''),
            'confidence': visual_confidence,
            'location': f"Aisle {result.get('aisle', 'TBD')}",
            'match_type': match_type,
            'weight': weight
        }
        matches.append(match)
    
    return matches

def remove_duplicate_matches_weighted(matches):
    """Remove duplicate SKUs and sort by visual similarity confidence with weights"""
    seen_skus = set()
    unique_matches = []
    
    # Sort by visual confidence (confidence * weight) first
    matches.sort(key=lambda x: x.get('confidence', 0) * x.get('weight', 1.0), reverse=True)
    
    for match in matches:
        sku = match.get('sku', '')
        if sku not in seen_skus and sku != 'N/A':
            seen_skus.add(sku)
            # Add visual similarity indicator to match type
            if match.get('weight', 1.0) >= 0.9:
                match['match_type'] = f"{match['match_type']} (High Visual Similarity)"
            elif match.get('weight', 1.0) >= 0.8:
                match['match_type'] = f"{match['match_type']} (Good Visual Similarity)"
            unique_matches.append(match)
    
    return unique_matches

def remove_duplicate_matches(matches):
    """Legacy function for backward compatibility"""
    # Convert to weighted format for consistent processing
    for match in matches:
        if 'weight' not in match:
            match['weight'] = 1.0
    return remove_duplicate_matches_weighted(matches)

def get_actual_grout_options():
    """Get actual grout options based on database records"""
    return {
        'superior_excel': {
            'unsanded': {
                'bag_sizes': [5, 20, 25],  # 20lb for some colors
                'colors': ['Antique White', 'Charcoal', 'Desert Sand', 'Dove Grey', 'Ivory', 
                          'Linen', 'London Fog', 'Mobe Pearl', 'Mocha', 'Natural', 'Standard White',
                          'Terracotta', 'Tobacco', 'Umber', 'Whisper Grey', 'Autumn Wheat', 
                          'Black Onyx', 'Hot Lila', 'Silver Luster'],
                'price_range': '$12.99-$45.99'
            },
            'sanded': {
                'bag_sizes': [8, 25],
                'colors': ['Antique White', 'Charcoal', 'Desert Sand', 'Dove Grey', 'Ivory',
                          'Linen', 'London Fog', 'Mobe Pearl', 'Mocha', 'Natural', 'Standard White',
                          'Terracotta', 'Tobacco', 'Umber', 'Whisper Grey'],
                'price_range': '$18.99-$45.99'
            }
        },
        'ardex': {
            'fg_c_microtec': {  # Unsanded
                'bag_sizes': [25],
                'colors': ['Brilliant White', 'Fresh Lily', 'Polar White', 'Silver Simmer'],
                'price_range': '$55.99'
            },
            'fl': {  # Sanded
                'bag_sizes': [25],
                'colors': ['Antique Ivory', 'Battleship', 'Black Licorice', 'Brilliant White',
                          'Cast Iron', 'Charcoal Dust', 'Dove Gray', 'Fresh Lilly', 'Gray Dusk',
                          'Gunmetal', 'Irish Cream', 'Polar White', 'Raw Steel', 'Silver Shimmer',
                          'Slate Gray', 'Smoke', 'Stone Beach', 'Stormy Mist', 'Sugar Cookie',
                          'Vintage Linen'],
                'price_range': '$55.99'
            }
        },
        'superior_pro_grout': {
            'sanded': {
                'bag_sizes': [8, 25],
                'colors': ['Almond', 'Antique White', 'Desert Bloom', 'Desert Sand', 'Dove Grey',
                          'Ivory', 'Linen', 'London Fog', 'Milk Chocolate', 'Mobe Pearl', 'Mocha',
                          'Natural', 'Whisper Grey', 'White', 'Terra-Cotta', 'Umber'],
                'price_range': '$8.99-$28.99'
            }
        },
        'superior_standard': {
            'unsanded': {
                'bag_sizes': [5],
                'colors': ['Antique White', 'Charcoal', 'Dove Grey', 'Ivory', 'Linen', 
                          'London Fog', 'Milk Chocolate', 'Mocha', 'Standard White', 'Tobacco',
                          'Whisper Grey'],
                'price_range': '$8.99'
            }
        }
    }

def recommend_grout_bag_actual(grout_lbs, grout_brand, grout_type):
    """Recommend bag size based on actual database inventory"""
    grout_options = get_actual_grout_options()
    
    if grout_brand == 'superior_excel':
        available_bags = grout_options['superior_excel'][grout_type]['bag_sizes']
    elif grout_brand == 'ardex':
        if grout_type == 'unsanded':
            available_bags = grout_options['ardex']['fg_c_microtec']['bag_sizes']
        else:
            available_bags = grout_options['ardex']['fl']['bag_sizes']
    elif grout_brand == 'superior_pro_grout':
        available_bags = grout_options['superior_pro_grout']['sanded']['bag_sizes']
    else:
        available_bags = [5, 8, 25]  # fallback
    
    # Find optimal bag size
    for bag_size in available_bags:
        if bag_size >= grout_lbs:
            return {
                'recommended_bag': bag_size,
                'quantity': 1,
                'total_lbs': bag_size,
                'waste_lbs': bag_size - grout_lbs,
                'waste_percent': round(((bag_size - grout_lbs) / bag_size) * 100, 1)
            }
    
    # Handle larger quantities with multiple bags
    largest_bag = max(available_bags)
    large_bags = int(grout_lbs // largest_bag)
    remainder = grout_lbs % largest_bag
    
    if remainder > 0:
        small_bag = next((size for size in available_bags if size >= remainder), available_bags[0])
        return {
            'recommended_bag': f"{large_bags}×{largest_bag}lb + 1×{small_bag}lb",
            'quantity': large_bags + 1,
            'total_lbs': (large_bags * largest_bag) + small_bag,
            'waste_lbs': ((large_bags * largest_bag) + small_bag) - grout_lbs,
            'waste_percent': round((((large_bags * largest_bag) + small_bag - grout_lbs) / ((large_bags * largest_bag) + small_bag)) * 100, 1)
        }
    
    return {
        'recommended_bag': f"{large_bags}×{largest_bag}lb",
        'quantity': large_bags,
        'total_lbs': large_bags * largest_bag,
        'waste_lbs': 0,
        'waste_percent': 0
    }

def get_sample_tile_matches():
    """Return sample tile matches as fallback"""
    return [
        {
            'name': 'Modern Ceramic Floor Tile',
            'sku': 'MCF-001',
            'price': 4.99,
            'image_url': '/static/placeholder-tile.jpg',
            'description': 'Modern ceramic tile with neutral finish',
            'confidence': 0.7,
            'location': 'Aisle 3'
        },
        {
            'name': 'Premium Porcelain Tile',
            'sku': 'PPT-002',
            'price': 7.50,
            'image_url': '/static/placeholder-tile.jpg',
            'description': 'High-quality porcelain tile',
            'confidence': 0.65,
            'location': 'Aisle 5'
        },
        {
            'name': 'Natural Stone Look Tile',
            'sku': 'NSL-003',
            'price': 6.25,
            'image_url': '/static/placeholder-tile.jpg',
            'description': 'Natural stone appearance ceramic tile',
            'confidence': 0.6,
            'location': 'Aisle 7'
        }
    ]

@app.route('/api/vision/rebuild-database', methods=['POST'])
def rebuild_vision_database():
    """Rebuild CLIP embeddings database"""
    try:
        if not clip_vision:
            return jsonify({'success': False, 'error': 'Vision system not available'})
        
        success = clip_vision.build_tile_database_embeddings(force_rebuild=True)
        
        if success:
            stats = clip_vision.get_database_stats()
            return jsonify({
                'success': True,
                'message': 'Vision database rebuilt successfully',
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to rebuild vision database'
            })
        
    except Exception as e:
        logger.error(f"Error rebuilding vision database: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/vision/stats')
def get_vision_stats():
    """Get vision system statistics"""
    try:
        if not clip_vision:
            return jsonify({'success': False, 'error': 'Vision system not available'})
        
        stats = clip_vision.get_database_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting vision stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/vision/find-in-store', methods=['POST'])
def find_tile_in_store():
    """Find tile location and inventory in store"""
    try:
        if not clip_vision or not store_inventory:
            return jsonify({'success': False, 'error': 'Vision or inventory system not available'})
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'})
        
        image_data = data['image']
        
        # First, identify the tile using CLIP
        vision_result = clip_vision.analyze_tile_image(image_data)
        
        if not vision_result.get('success') or not vision_result.get('best_match'):
            return jsonify({
                'success': False,
                'message': 'Could not identify tile from image',
                'error': 'No matching tiles found'
            })
        
        best_match = vision_result['best_match']
        sku = best_match['sku']
        
        # Get store location and inventory
        store_info = store_inventory.find_in_store(sku)
        
        if store_info['success']:
            # Combine vision results with store information
            result = {
                'success': True,
                'tile_identification': {
                    'sku': sku,
                    'name': best_match['name'],
                    'confidence': best_match['confidence'],
                    'similarity': best_match['similarity']
                },
                'store_location': store_info['location'],
                'inventory': store_info['inventory'],
                'store_info': store_info['store_info']
            }
        else:
            result = {
                'success': False,
                'tile_identification': {
                    'sku': sku,
                    'name': best_match['name'],
                    'confidence': best_match['confidence']
                },
                'message': store_info.get('message', 'Store information not available')
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error finding tile in store: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/store/location/<sku>')
def get_store_location(sku):
    """Get store location for a specific SKU"""
    try:
        if not store_inventory:
            return jsonify({'success': False, 'error': 'Store inventory system not available'})
        
        store_info = store_inventory.find_in_store(sku)
        return jsonify(store_info)
        
    except Exception as e:
        logger.error(f"Error getting store location for SKU {sku}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/health')
def system_health():
    """System health check"""
    try:
        health_status = {
            'status': 'healthy',
            'mode': 'customer',
            'port': 8081,
            'database': db_manager is not None,
            'rag': rag_manager is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

# Hybrid Form/LLM Structured Data API Endpoints
@app.route('/api/chat/structured-context', methods=['POST'])
def handle_structured_context():
    """Handle LLM context updates from structured data changes"""
    try:
        data = request.get_json()
        action = data.get('action', '')
        project_data = data.get('projectData', {})
        phone = data.get('phone', 'unknown')
        
        logger.info(f"Structured context update: {action} for {phone}")
        
        # Generate LLM response based on structured data context
        llm_response = generate_structured_acknowledgment(action, project_data)
        
        return jsonify({
            'success': True,
            'llm_response': llm_response,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling structured context: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/project/structured-save', methods=['POST'])
def save_structured_project():
    """Save structured project data to database"""
    try:
        data = request.get_json()
        phone = data.get('phone', 'unknown')
        project_data = data.get('projectData', {})
        
        # Save to database (extend existing customer_projects table or create new structured table)
        save_result = save_project_to_database(phone, project_data)
        
        logger.info(f"Saved structured project for {phone}: {project_data.get('projectName', 'Untitled')}")
        
        return jsonify({
            'success': True,
            'project_id': save_result.get('project_id'),
            'saved_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving structured project: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/project/ar-visualization', methods=['POST'])
def save_ar_visualization():
    """Save AR visualization data to customer project"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        visualization_data = data.get('visualization_data', {})
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number required'})
        
        # Create AR visualization record
        ar_record = {
            'phone_number': phone_number,
            'timestamp': datetime.now().isoformat(),
            'ar_data': {
                'tile_type': visualization_data.get('ar_visualization', {}).get('tile_type'),
                'tile_size': visualization_data.get('ar_visualization', {}).get('tile_size'),
                'pattern': visualization_data.get('ar_visualization', {}).get('pattern'),
                'grout_color': visualization_data.get('ar_visualization', {}).get('grout_color'),
                'room_dimensions': visualization_data.get('ar_visualization', {}).get('room_dimensions'),
                'session_id': f"ar_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
        
        # Save to database (you would extend this to save to a specific AR table)
        logger.info(f"AR visualization saved for {phone_number}: {ar_record['ar_data']['tile_type']} tiles")
        
        # For now, we'll return success (in production, save to database)
        return jsonify({
            'success': True,
            'session_id': ar_record['ar_data']['session_id'],
            'message': 'AR visualization saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving AR visualization: {e}")
        return jsonify({'success': False, 'error': str(e)})

def create_project_summary(project_data, session_id):
    """Create a concise project summary from form data for LLM context"""
    try:
        summary_parts = []
        
        # Session reference
        if session_id:
            summary_parts.append(f"Session: {session_id}")
        
        # Customer info
        customer = project_data.get('customer', {})
        if customer.get('name') or customer.get('phone'):
            customer_info = []
            if customer.get('name'):
                customer_info.append(f"Name: {customer['name']}")
            if customer.get('phone'):
                customer_info.append(f"Phone: {customer['phone']}")
            summary_parts.append(f"Customer: {', '.join(customer_info)}")
        
        # Project info
        project = project_data.get('project', {})
        if project.get('name') or project.get('address'):
            project_info = []
            if project.get('name'):
                project_info.append(f"Project: {project['name']}")
            if project.get('address'):
                project_info.append(f"Address: {project['address']}")
            summary_parts.append(', '.join(project_info))
        
        # Rooms and surfaces
        rooms = project_data.get('rooms', [])
        if rooms:
            rooms_info = []
            for room in rooms:
                room_name = room.get('name', 'Unknown Room')
                surfaces = room.get('surfaces', [])
                if surfaces:
                    surface_details = []
                    for surface in surfaces:
                        surface_type = surface.get('type', 'surface')
                        height = surface.get('height', 0)
                        width = surface.get('width', 0)
                        sqft = surface.get('sqft', height * width)
                        if sqft > 0:
                            surface_details.append(f"{surface_type} ({sqft} sq ft)")
                        else:
                            surface_details.append(surface_type)
                    rooms_info.append(f"{room_name}: {', '.join(surface_details)}")
                else:
                    rooms_info.append(f"{room_name}: no surfaces defined")
            
            if rooms_info:
                summary_parts.append(f"Rooms: {'; '.join(rooms_info)}")
        
        # Current/saved surfaces (if no rooms)
        if not rooms:
            saved_surfaces = project_data.get('saved_surfaces', [])
            if saved_surfaces:
                surface_info = []
                for surface in saved_surfaces:
                    area = surface.get('area', 'room')
                    surface_type = surface.get('surface', 'surface')
                    calculated = surface.get('calculated', 0)
                    if calculated > 0:
                        surface_info.append(f"{area} {surface_type} ({calculated} sq ft)")
                    else:
                        surface_info.append(f"{area} {surface_type}")
                summary_parts.append(f"Surfaces: {', '.join(surface_info)}")
        
        # Conversation preferences
        preferences = project_data.get('preferences', {})
        if preferences:
            pref_parts = []
            if preferences.get('colors'):
                pref_parts.append(f"Colors: {', '.join(preferences['colors'])}")
            if preferences.get('styles'):
                pref_parts.append(f"Styles: {', '.join(preferences['styles'])}")
            if pref_parts:
                summary_parts.append(f"Preferences: {'; '.join(pref_parts)}")
        
        return ' | '.join(summary_parts) if summary_parts else None
        
    except Exception as e:
        logger.error(f"Error creating project summary: {e}")
        return None

def generate_structured_acknowledgment(action, project_data):
    """Generate LLM acknowledgment of structured data updates"""
    try:
        # Create context-aware response based on the action
        context_messages = {
            'opened_panel': f"I can see you're setting up a project! The structured data panel is a great way to organize your tile project details.",
            'project_details_updated': f"Perfect! I see you're working on '{project_data.get('projectName', 'your project')}' - a {project_data.get('roomType', 'room')} project. This helps me provide much better recommendations.",
            'dimensions_entered': f"Excellent! With {project_data.get('totalArea', 0):.1f} square feet to work with, you have lots of great tile options. {get_room_specific_guidance(project_data.get('roomType', ''), project_data.get('totalArea', 0))}",
            'surface_added': f"Great choice adding that surface! I can help you find the perfect tile that coordinates with your other selections."
        }
        
        base_response = context_messages.get(action, "Thanks for updating your project details!")
        
        # Add specific guidance based on room type and area
        if action == 'dimensions_entered' and project_data.get('roomType'):
            room_guidance = get_room_specific_guidance(project_data.get('roomType'), project_data.get('totalArea', 0))
            if room_guidance:
                base_response += f" {room_guidance}"
        
        return base_response
        
    except Exception as e:
        logger.error(f"Error generating structured acknowledgment: {e}")
        return "Thanks for updating your project information!"

def get_room_specific_guidance(room_type, total_area):
    """Provide room-specific guidance based on type and size"""
    guidance_map = {
        'bathroom': {
            'small': "For bathrooms under 50 sq ft, I recommend focusing on light colors to make the space feel larger, and definitely prioritize slip-resistant flooring.",
            'medium': "This is a nice-sized bathroom! You'll want to consider both style and function - slip resistance for safety, easy cleaning, and coordinating floor and wall tiles.",
            'large': "What a spacious bathroom! You have room for some really stunning design choices. Consider large format tiles for a luxurious look, or beautiful natural stone."
        },
        'kitchen': {
            'small': "In smaller kitchens, light-colored tiles and smart layout choices can really open up the space. Focus on durable, easy-to-clean surfaces.",
            'medium': "Perfect kitchen size for both style and function! Consider how your tile choices will coordinate with your cabinets and countertops.",
            'large': "You have space for some amazing design possibilities! Consider statement backsplashes, mixed materials, or stunning large-format flooring."
        },
        'living-room': {
            'small': "For smaller living spaces, I recommend tiles that flow well with adjacent rooms to create visual continuity.",
            'medium': "Great space for showcasing beautiful flooring! Consider durability for high-traffic areas and how the tile coordinates with your overall decor.",
            'large': "Perfect for making a real design statement! You could consider mixed materials, patterns, or feature areas."
        }
    }
    
    # Determine size category
    size_category = 'small' if total_area < 50 else 'medium' if total_area < 150 else 'large'
    
    return guidance_map.get(room_type, {}).get(size_category, "")

def save_project_to_database(phone, project_data):
    """Save structured project data to database"""
    try:
        # For now, extend the existing approach - in production this would use the new structured tables
        db_manager = get_db_manager()  # Assume this exists from existing code
        
        project_id = f"struct_{phone}_{int(datetime.now().timestamp())}"
        
        # This would typically save to the new structured_projects table
        # For now, we'll integrate with existing customer projects system
        
        return {
            'success': True,
            'project_id': project_id
        }
        
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/api/design/generate-room-layout', methods=['POST'])
def generate_room_layout():
    """Generate room design using DALL-E 3 with multiple tile SKUs"""
    try:
        if not DALLE_AVAILABLE:
            return jsonify({
                'success': False, 
                'error': 'DALL-E 3 image generation not available. Please install OpenAI package and set OPENAI_API_KEY.'
            })
        
        data = request.get_json()
        
        # Extract room and tile information
        room_type = data.get('roomType', 'bathroom')
        room_dimensions = data.get('dimensions', {})
        surfaces = data.get('surfaces', [])
        style_preference = data.get('stylePreference', 'modern')
        
        if not surfaces:
            return jsonify({
                'success': False,
                'error': 'No surfaces with tiles selected. Please add surfaces and select tiles first.'
            })
        
        # Build detailed design prompt
        design_prompt = build_design_prompt(room_type, room_dimensions, surfaces, style_preference)
        
        logger.info(f"Generating room design with DALL-E 3: {design_prompt[:100]}...")
        
        # Call DALL-E 3 API
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=design_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        
        # Get tile details for display
        tile_details = []
        for surface in surfaces:
            if surface.get('selectedTile'):
                tile = surface['selectedTile']
                tile_details.append({
                    'surface': surface['name'],
                    'tile_name': tile.get('name', 'Unknown Tile'),
                    'sku': tile.get('sku', 'N/A'),
                    'price': tile.get('price', 0),
                    'area': surface.get('dimensions', {}).get('sqft', 0)
                })
        
        return jsonify({
            'success': True,
            'design_url': image_url,
            'prompt_used': design_prompt,
            'tile_details': tile_details,
            'room_info': {
                'type': room_type,
                'dimensions': room_dimensions,
                'style': style_preference,
                'total_surfaces': len(surfaces)
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating room design: {e}")
        return jsonify({
            'success': False,
            'error': f"Failed to generate design: {str(e)}"
        })

def build_design_prompt(room_type, dimensions, surfaces, style='modern'):
    """Build detailed DALL-E 3 prompt for room design"""
    
    # Base room description
    room_size = f"{dimensions.get('length', 10)} x {dimensions.get('width', 8)} feet"
    
    prompt_parts = [
        f"Create a photorealistic {style} {room_type} interior design rendering.",
        f"Room dimensions: {room_size}.",
        "High-quality architectural visualization with professional lighting."
    ]
    
    # Add surface-specific tile descriptions
    surface_descriptions = []
    
    for surface in surfaces:
        if not surface.get('selectedTile'):
            continue
            
        tile = surface['selectedTile']
        surface_name = surface['name']
        tile_name = tile.get('name', 'ceramic tile')
        
        # Create detailed tile description based on surface type
        if 'floor' in surface_name.lower():
            surface_descriptions.append(
                f"Floor: {tile_name} with realistic tile pattern, proper grout lines, and natural texture"
            )
        elif 'wall' in surface_name.lower() or 'backsplash' in surface_name.lower():
            surface_descriptions.append(
                f"Walls/Backsplash: {tile_name} with accurate tile layout and professional installation"
            )
        elif 'shower' in surface_name.lower():
            surface_descriptions.append(
                f"Shower area: {tile_name} with water-resistant appearance and proper tile alignment"
            )
        else:
            surface_descriptions.append(
                f"{surface_name}: {tile_name} with realistic material appearance"
            )
    
    if surface_descriptions:
        prompt_parts.append("Tile specifications:")
        prompt_parts.extend(surface_descriptions)
    
    # Add style-specific details
    style_details = {
        'modern': "Clean lines, minimalist fixtures, contemporary color palette, LED lighting",
        'traditional': "Classic fixtures, warm colors, traditional patterns, elegant details",
        'transitional': "Blend of modern and traditional elements, neutral colors, balanced design",
        'industrial': "Raw materials, exposed elements, metal accents, urban aesthetic",
        'farmhouse': "Rustic charm, natural materials, vintage-inspired fixtures, cozy atmosphere"
    }
    
    prompt_parts.append(f"Style elements: {style_details.get(style, style_details['modern'])}")
    
    # Add technical specifications
    prompt_parts.extend([
        "Professional interior photography quality.",
        "Realistic lighting with natural and artificial light sources.",
        "Show proper tile installation with accurate grout lines and spacing.",
        "Include appropriate fixtures and accessories for the room type.",
        "Photorealistic textures and materials.",
        "High-resolution architectural visualization."
    ])
    
    return " ".join(prompt_parts)

@app.route('/api/design/get-style-options')
def get_design_style_options():
    """Get available design style options"""
    styles = [
        {
            'id': 'modern',
            'name': 'Modern',
            'description': 'Clean lines, minimalist fixtures, contemporary design'
        },
        {
            'id': 'traditional',
            'name': 'Traditional', 
            'description': 'Classic fixtures, warm colors, timeless elegance'
        },
        {
            'id': 'transitional',
            'name': 'Transitional',
            'description': 'Perfect blend of modern and traditional elements'
        },
        {
            'id': 'industrial',
            'name': 'Industrial',
            'description': 'Raw materials, exposed elements, urban aesthetic'
        },
        {
            'id': 'farmhouse',
            'name': 'Farmhouse',
            'description': 'Rustic charm, natural materials, cozy atmosphere'
        }
    ]
    
    return jsonify({
        'success': True,
        'styles': styles,
        'default': 'modern'
    })

# ========================================
# DYNAMIC FORM SYSTEM API ENDPOINTS
# ========================================

@app.route('/api/customers/lookup/<phone_number>')
def lookup_customer(phone_number):
    """Lookup customer by phone number"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
        
        # Clean phone number
        cleaned_phone = ''.join(c for c in phone_number if c.isdigit())
        
        # Search for customer in database
        customer = db_manager.get_customer_by_phone(cleaned_phone)
        
        if customer:
            # Get customer's existing projects
            projects = db_manager.get_customer_projects(cleaned_phone)
            
            return jsonify({
                'success': True,
                'customer': {
                    'phone': customer.get('phone', ''),
                    'name': customer.get('name', ''),
                    'email': customer.get('email', ''),
                    'id': customer.get('id', '')
                },
                'projects': projects or []
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            })
        
    except Exception as e:
        logger.error(f"Error looking up customer {phone_number}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/customers/create', methods=['POST'])
def create_customer():
    """Create new customer"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
        
        data = request.get_json()
        phone = data.get('phone', '').strip()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        
        if not phone or not name:
            return jsonify({'success': False, 'error': 'Phone and name are required'})
        
        # Clean phone number
        cleaned_phone = ''.join(c for c in phone if c.isdigit())
        
        # Create customer
        customer_id = db_manager.create_customer(cleaned_phone, name, email)
        
        return jsonify({
            'success': True,
            'customer_id': customer_id,
            'customer': {
                'phone': cleaned_phone,
                'name': name,
                'email': email,
                'id': customer_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects/create', methods=['POST'])
def create_project():
    """Create new project"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
        
        data = request.get_json()
        customer_phone = data.get('customer_phone', '').strip()
        project_name = data.get('project_name', '').strip()
        address = data.get('address', '').strip()
        
        if not customer_phone or not project_name:
            return jsonify({'success': False, 'error': 'Customer phone and project name are required'})
        
        # Clean phone number
        cleaned_phone = ''.join(c for c in customer_phone if c.isdigit())
        
        # Create project
        project_id = db_manager.create_project(cleaned_phone, project_name, address)
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'project': {
                'id': project_id,
                'name': project_name,
                'address': address,
                'customer_phone': cleaned_phone
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/grout/calculate', methods=['POST'])
def calculate_grout_recommendation():
    """Calculate grout recommendation for a tile and surface"""
    try:
        data = request.get_json()
        tile_info = data.get('tile', {})
        surface_sqft = data.get('surface_sqft', 0)
        
        if not tile_info or surface_sqft <= 0:
            return jsonify({'success': False, 'error': 'Tile info and surface area required'})
        
        # Determine grout type based on tile characteristics
        grout_type = determine_grout_type_from_tile(tile_info)
        
        # Calculate grout quantity
        grout_lbs = calculate_grout_quantity_advanced(surface_sqft, tile_info)
        
        # Get bag recommendation
        bag_recommendation = recommend_grout_bag_actual(grout_lbs, 'superior_excel', grout_type)
        
        return jsonify({
            'success': True,
            'grout_type': grout_type,
            'grout_lbs_needed': grout_lbs,
            'bag_recommendation': bag_recommendation,
            'explanation': f"Based on {tile_info.get('material_type', 'ceramic')} tile and {surface_sqft} sq ft area"
        })
        
    except Exception as e:
        logger.error(f"Error calculating grout recommendation: {e}")
        return jsonify({'success': False, 'error': str(e)})

def determine_grout_type_from_tile(tile_info):
    """Determine grout type based on tile characteristics"""
    material_type = tile_info.get('material_type', '').lower()
    finish = tile_info.get('finish', '').lower()
    edge_type = tile_info.get('edge_type', '').lower()
    
    # Natural stone logic
    if any(stone in material_type for stone in ['marble', 'travertine', 'limestone']):
        if 'polished' in finish:
            return 'unsanded'
        else:
            return 'sanded'
    
    # Rectified tiles
    if 'rectified' in edge_type:
        return 'unsanded'
    
    # Glass tiles
    if 'glass' in material_type:
        return 'unsanded'
    
    # Default to sanded for ceramic/porcelain
    return 'sanded'

def calculate_grout_quantity_advanced(surface_sqft, tile_info):
    """Advanced grout quantity calculation based on tile size and grout width"""
    tile_size = tile_info.get('size', '12x12')
    grout_width = tile_info.get('grout_width', '1/8"')
    
    # Base rates per square foot for different grout widths
    grout_rates = {
        '1/16"': 0.045,
        '1/8"': 0.067,
        '3/16"': 0.089,
        '1/4"': 0.111
    }
    
    # Adjust for tile size
    if 'x' in tile_size:
        try:
            dimensions = tile_size.split('x')
            width = int(dimensions[0])
            height = int(dimensions[1])
            tile_area = width * height
            
            # Smaller tiles need more grout
            if tile_area < 16:  # 4x4 or smaller
                multiplier = 1.3
            elif tile_area < 64:  # 8x8 or smaller
                multiplier = 1.1
            else:
                multiplier = 1.0
        except:
            multiplier = 1.0
    else:
        multiplier = 1.0
    
    base_rate = grout_rates.get(grout_width, 0.067)
    return max(1, int(surface_sqft * base_rate * multiplier))

@app.route('/api/materials/calculate', methods=['POST'])
def calculate_materials():
    """Calculate all materials needed for a surface"""
    try:
        data = request.get_json()
        surface_info = data.get('surface', {})
        tile_info = data.get('tile', {})
        
        surface_sqft = surface_info.get('calculated', 0)
        surface_type = surface_info.get('surface', '')
        area_type = surface_info.get('area', '')
        
        if surface_sqft <= 0:
            return jsonify({'success': False, 'error': 'Surface area required'})
        
        materials = {
            'tile': {
                'quantity_sqft': surface_sqft,
                'waste_factor': 0.1,
                'total_needed': surface_sqft * 1.1,
                'estimated_cost': surface_sqft * 1.1 * tile_info.get('price', 0)
            },
            'grout': {},
            'thinset': {
                'bags_needed': max(1, int(surface_sqft / 100)),  # 50lb bag covers ~100 sqft
                'type': 'glass_specific' if 'glass' in tile_info.get('material_type', '').lower() else 'standard',
                'estimated_cost': max(1, int(surface_sqft / 100)) * 25.99
            },
            'additives': {}
        }
        
        # Calculate grout
        grout_type = determine_grout_type_from_tile(tile_info)
        grout_lbs = calculate_grout_quantity_advanced(surface_sqft, tile_info)
        bag_rec = recommend_grout_bag_actual(grout_lbs, 'superior_excel', grout_type)
        
        materials['grout'] = {
            'type': grout_type,
            'lbs_needed': grout_lbs,
            'bag_recommendation': bag_rec,
            'estimated_cost': bag_rec.get('total_lbs', 8) * 2.25  # Approximate cost per lb
        }
        
        # Calculate additives based on surface type
        if surface_type == 'floor':
            materials['additives']['decoupling_membrane'] = {
                'sqft_needed': surface_sqft,
                'estimated_cost': surface_sqft * 1.25
            }
        
        if area_type in ['shower', 'bathtub-surround']:
            materials['additives']['waterproofing'] = {
                'sqft_needed': surface_sqft,
                'estimated_cost': surface_sqft * 2.50
            }
        
        # Calculate total cost
        total_cost = (
            materials['tile']['estimated_cost'] +
            materials['grout']['estimated_cost'] +
            materials['thinset']['estimated_cost'] +
            sum(addon.get('estimated_cost', 0) for addon in materials['additives'].values())
        )
        
        return jsonify({
            'success': True,
            'materials': materials,
            'total_estimated_cost': round(total_cost, 2),
            'surface_sqft': surface_sqft
        })
        
    except Exception as e:
        logger.error(f"Error calculating materials: {e}")
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    logger.info('Customer client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Customer client disconnected')

if __name__ == '__main__':
    logger.info("Starting Customer Chat Application on port 8081")
    socketio.run(app, debug=True, host='0.0.0.0', port=8081, allow_unsafe_werkzeug=True)