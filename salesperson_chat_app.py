#!/usr/bin/env python3
"""
Salesperson Chat Application - Port 8082
SKU search, tile finder, image generation, upsell reminders, project organization
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
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'salesperson-chat-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
try:
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    logger.info("Salesperson chat components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    db_manager = None
    rag_manager = None

class SalespersonAgent:
    """Specialized agent for salesperson workflows"""
    
    def __init__(self, db_manager, rag_manager):
        self.db = db_manager
        self.rag = rag_manager
        
    def search_by_sku(self, sku):
        """Search for products by SKU"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
                
            # Search for product by SKU
            products = self.db.search_products_by_sku(sku)
            
            if products:
                product = products[0]
                return {
                    "success": True,
                    "product": product,
                    "upsell_suggestions": self._get_upsell_suggestions(product),
                    "installation_materials": self._get_installation_materials(product)
                }
            else:
                return {"success": False, "error": f"No product found with SKU: {sku}"}
                
        except Exception as e:
            logger.error(f"Error searching by SKU: {e}")
            return {"success": False, "error": str(e)}
    
    def find_tiles_by_criteria(self, room_type, style, size=None, color=None, price_range=None):
        """Find tiles based on specific criteria"""
        try:
            if not self.rag:
                return {"success": False, "error": "RAG system not available"}
                
            # Build search query
            search_parts = [room_type, style]
            if size:
                search_parts.append(f"{size} size")
            if color:
                search_parts.append(f"{color} color")
            if price_range:
                search_parts.append(f"price {price_range}")
                
            query = " ".join(search_parts)
            
            # Search using RAG
            results = self.rag.search(query, limit=10)
            
            return {
                "success": True,
                "tiles": results,
                "search_query": query,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error finding tiles: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_project_materials(self, dimensions, tile_sku, pattern="straight"):
        """Calculate materials needed for a project"""
        try:
            # Parse dimensions
            import re
            dimension_match = re.search(r'(\d+\.?\d*)\s*[x×by]\s*(\d+\.?\d*)', dimensions.lower())
            if not dimension_match:
                return {"success": False, "error": "Could not parse dimensions"}
                
            length = float(dimension_match.group(1))
            width = float(dimension_match.group(2))
            area = length * width
            
            # Waste factors by pattern
            waste_factors = {
                "straight": 0.10,
                "diagonal": 0.15,
                "herringbone": 0.20,
                "complex": 0.20
            }
            
            waste_factor = waste_factors.get(pattern, 0.10)
            total_area = area * (1 + waste_factor)
            
            # Get tile info
            tile_info = self.search_by_sku(tile_sku)
            
            materials = {
                "tile_area_needed": total_area,
                "waste_factor": waste_factor,
                "base_area": area,
                "pattern": pattern
            }
            
            if tile_info["success"]:
                product = tile_info["product"]
                materials.update({
                    "tile_name": product.get("product_name", ""),
                    "tile_price_per_sf": product.get("price_per_square_foot", 0),
                    "estimated_tile_cost": total_area * (product.get("price_per_square_foot", 0) or 0)
                })
            
            return {
                "success": True,
                "materials": materials,
                "upsells": self._get_installation_upsells(total_area)
            }
            
        except Exception as e:
            logger.error(f"Error calculating materials: {e}")
            return {"success": False, "error": str(e)}
    
    def get_customer_projects(self, phone_number):
        """Get all projects for a customer organized by room"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
                
            # Get customer conversations and organize by project/room
            conversations = self.db.get_customer_conversations(phone_number)
            
            # Group by room_type and project
            projects = {}
            for conv in conversations:
                room_type = conv.get('room_type', 'General')
                project_name = conv.get('project_name', 'Main Project')
                
                if room_type not in projects:
                    projects[room_type] = {}
                if project_name not in projects[room_type]:
                    projects[room_type][project_name] = []
                    
                projects[room_type][project_name].append(conv)
            
            return {
                "success": True,
                "customer_phone": phone_number,
                "projects": projects,
                "total_rooms": len(projects),
                "total_conversations": len(conversations)
            }
            
        except Exception as e:
            logger.error(f"Error getting customer projects: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_upsell_suggestions(self, product):
        """Get upsell suggestions for a product"""
        upsells = []
        
        if "tile" in product.get("product_name", "").lower():
            upsells.extend([
                {"item": "Premium Grout", "reason": "Enhanced durability and stain resistance"},
                {"item": "Grout Sealer", "reason": "Long-term protection and maintenance"},
                {"item": "Tile Spacers", "reason": "Professional installation spacing"},
                {"item": "Leveling System", "reason": "Perfect tile alignment"}
            ])
            
        if "porcelain" in product.get("material", "").lower():
            upsells.append({"item": "Diamond Blade", "reason": "Clean cuts for porcelain"})
            
        return upsells
    
    def _get_installation_materials(self, product):
        """Get installation materials for a product"""
        materials = [
            {"item": "Thinset Adhesive", "essential": True},
            {"item": "Grout", "essential": True},
            {"item": "Tile Spacers", "essential": True}
        ]
        
        if "natural stone" in product.get("material", "").lower():
            materials.append({"item": "Stone Sealer", "essential": True})
            
        return materials
    
    def _get_installation_upsells(self, total_area):
        """Get upsell suggestions based on project size"""
        upsells = []
        
        if total_area > 100:
            upsells.append({"item": "Professional Installation", "reason": "Large project complexity"})
            
        upsells.extend([
            {"item": "Underlayment", "reason": "Smooth surface preparation"},
            {"item": "Transition Strips", "reason": "Professional edge finishing"},
            {"item": "Maintenance Kit", "reason": "Long-term care and protection"}
        ])
        
        return upsells

@app.route('/')
def index():
    """Home page redirect to sales-chat"""
    return render_template('salesperson_chat.html')

@app.route('/sales-chat')
def sales_chat():
    """Salesperson chat interface"""
    return render_template('salesperson_chat.html')

@app.route('/chat')
def chat():
    """Legacy chat route - redirect to sales-chat"""
    return render_template('salesperson_chat.html')

@app.route('/api/chat', methods=['POST'])
def salesperson_chat_api():
    """Salesperson-focused chat endpoint with NEPQ scoring"""
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
        
        # Initialize Simple Tile Agent with NEPQ scoring
        agent = SimpleTileAgent(db_manager, rag_manager)
        
        # Process with NEPQ scoring
        result = agent.process_customer_query(
            query, 
            conversation_history,
            customer_phone=customer_phone,
            customer_name=customer_name
        )
        
        # Generate self-analysis report if conversation is substantial
        self_analysis = None
        if len(conversation_history) >= 3:
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
            'mode': 'salesperson',
            'aos_phase': result.get('aos_phase', 'discovery'),
            'requirements_complete': result.get('requirements_complete', False),
            'nepq_analysis': result.get('nepq_analysis', {}),
            'self_analysis': self_analysis
        })
        
    except Exception as e:
        logger.error(f"Error in salesperson chat: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/search/sku', methods=['POST'])
def search_sku():
    """Search by SKU endpoint"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
            
        data = request.get_json()
        sku = data.get('sku', '').strip()
        
        if not sku:
            return jsonify({'success': False, 'error': 'SKU is required'})
        
        agent = SalespersonAgent(db_manager, rag_manager)
        result = agent.search_by_sku(sku)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in SKU search: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tiles/find', methods=['POST'])
def find_tiles():
    """Find tiles by criteria"""
    try:
        if not rag_manager:
            return jsonify({'success': False, 'error': 'RAG system not available'})
            
        data = request.get_json()
        room_type = data.get('room_type', '')
        style = data.get('style', '')
        size = data.get('size', '')
        color = data.get('color', '')
        price_range = data.get('price_range', '')
        
        agent = SalespersonAgent(db_manager, rag_manager)
        result = agent.find_tiles_by_criteria(room_type, style, size, color, price_range)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error finding tiles: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/materials/calculate', methods=['POST'])
def calculate_materials():
    """Calculate project materials"""
    try:
        data = request.get_json()
        dimensions = data.get('dimensions', '')
        tile_sku = data.get('tile_sku', '')
        pattern = data.get('pattern', 'straight')
        
        agent = SalespersonAgent(db_manager, rag_manager)
        result = agent.calculate_project_materials(dimensions, tile_sku, pattern)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error calculating materials: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/customer/projects/<phone_number>')
def get_customer_projects(phone_number):
    """Get customer projects organized by room"""
    try:
        if not db_manager:
            return jsonify({'success': False, 'error': 'Database not available'})
            
        agent = SalespersonAgent(db_manager, rag_manager)
        result = agent.get_customer_projects(phone_number)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting customer projects: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/image/generate', methods=['POST'])
def generate_tile_image():
    """Generate or retrieve tile visualization image"""
    try:
        data = request.get_json()
        tile_sku = data.get('tile_sku', '')
        room_type = data.get('room_type', 'bathroom')
        style = data.get('style', 'modern')
        
        # For now, return a placeholder implementation
        # In production, this would integrate with an image generation service
        
        return jsonify({
            'success': True,
            'image_url': f'https://via.placeholder.com/800x600/cccccc/333333?text=Tile+{tile_sku}+in+{room_type}',
            'tile_sku': tile_sku,
            'room_type': room_type,
            'style': style,
            'generated': True
        })
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/health')
def system_health():
    """System health check"""
    try:
        health_status = {
            'status': 'healthy',
            'mode': 'salesperson',
            'port': 8082,
            'database': db_manager is not None,
            'rag': rag_manager is not None,
            'features': [
                'sku_search',
                'tile_finder',
                'material_calculator',
                'customer_projects',
                'upsell_reminders',
                'image_generation'
            ],
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
    logger.info('Salesperson client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Salesperson client disconnected')

if __name__ == '__main__':
    logger.info("Starting Salesperson Chat Application on port 8082")
    socketio.run(app, debug=True, host='0.0.0.0', port=8082)