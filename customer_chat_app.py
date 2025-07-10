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
from modules.clip_tile_vision import CLIPTileVision
from modules.store_inventory import StoreInventoryManager

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
    clip_vision = CLIPTileVision(db_manager)
    store_inventory = StoreInventoryManager(db_manager)
    logger.info("Customer chat components initialized successfully")
    
    # Build tile embeddings in background
    logger.info("Building CLIP tile database embeddings...")
    clip_vision.build_tile_database_embeddings()
    logger.info("CLIP tile vision system ready")
    
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

@socketio.on('connect')
def handle_connect():
    logger.info('Customer client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Customer client disconnected')

if __name__ == '__main__':
    logger.info("Starting Customer Chat Application on port 8081")
    socketio.run(app, debug=True, host='0.0.0.0', port=8081)