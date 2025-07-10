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
    logger.info("Customer chat components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    db_manager = None
    rag_manager = None

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
        
        return jsonify({
            'success': True,
            'response': result.get('response', ''),
            'tool_calls': result.get('tool_calls', []),
            'mode': 'customer',
            'aos_phase': result.get('aos_phase', 'discovery'),
            'requirements_complete': result.get('requirements_complete', False)
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