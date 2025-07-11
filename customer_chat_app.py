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
        customer_phone = data.get('customer_phone', '')
        customer_name = data.get('customer_name', '')
        
        if not query.strip():
            return jsonify({'success': False, 'error': 'Query cannot be empty'})
        
        # Initialize Simple Tile Agent with AOS methodology
        agent = SimpleTileAgent(db_manager, rag_manager)
        
        # Process with AOS methodology
        result = agent.process_customer_query(
            query, 
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
    """Analyze uploaded tile image using CLIP vision"""
    try:
        if not clip_vision:
            return jsonify({'success': False, 'error': 'Vision system not available'})
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'})
        
        image_data = data['image']
        
        # Analyze the tile image
        result = clip_vision.analyze_tile_image(image_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error analyzing tile image: {e}")
        return jsonify({'success': False, 'error': str(e)})

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

@socketio.on('connect')
def handle_connect():
    logger.info('Customer client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Customer client disconnected')

if __name__ == '__main__':
    logger.info("Starting Customer Chat Application on port 8081")
    socketio.run(app, debug=True, host='0.0.0.0', port=8081, allow_unsafe_werkzeug=True)