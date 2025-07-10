#!/usr/bin/env python3
"""
Contractor Chat Application - Port 8083
Installation-focused tools, technical specifications, material calculators
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import json
import logging
import math
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
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'contractor-chat-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
try:
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    logger.info("Contractor chat components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    db_manager = None
    rag_manager = None

class ContractorAgent:
    """Specialized agent for contractor workflows"""
    
    def __init__(self, db_manager, rag_manager):
        self.db = db_manager
        self.rag = rag_manager
        
    def get_installation_guide(self, product_sku):
        """Get detailed installation instructions for a product"""
        try:
            if not self.rag:
                return {"success": False, "error": "RAG system not available"}
                
            # Search for installation guides
            query = f"installation guide instructions {product_sku}"
            results = self.rag.search(query, limit=5)
            
            # Get product technical specs
            tech_specs = self._get_technical_specs(product_sku)
            
            return {
                "success": True,
                "product_sku": product_sku,
                "installation_guides": results,
                "technical_specs": tech_specs,
                "required_tools": self._get_required_tools(product_sku),
                "preparation_steps": self._get_preparation_steps(product_sku)
            }
            
        except Exception as e:
            logger.error(f"Error getting installation guide: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_advanced_materials(self, project_data):
        """Advanced material calculations for contractors"""
        try:
            # Parse project data
            dimensions = project_data.get('dimensions', '')
            tile_sku = project_data.get('tile_sku', '')
            pattern = project_data.get('pattern', 'straight')
            substrate = project_data.get('substrate', 'concrete')
            tile_size = project_data.get('tile_size', '12x12')
            
            # Calculate base area
            import re
            dimension_match = re.search(r'(\d+\.?\d*)\s*[x×by]\s*(\d+\.?\d*)', dimensions.lower())
            if not dimension_match:
                return {"success": False, "error": "Could not parse dimensions"}
                
            length = float(dimension_match.group(1))
            width = float(dimension_match.group(2))
            area = length * width
            
            # Advanced waste calculations
            waste_factors = self._get_advanced_waste_factors(pattern, tile_size, substrate)
            total_area = area * (1 + waste_factors['total_waste'])
            
            # Calculate all materials
            materials = self._calculate_all_materials(area, total_area, tile_size, substrate, pattern)
            
            # Calculate labor estimates
            labor_estimates = self._calculate_labor_estimates(area, pattern, substrate)
            
            return {
                "success": True,
                "project_area": area,
                "total_area_with_waste": total_area,
                "waste_factors": waste_factors,
                "materials": materials,
                "labor_estimates": labor_estimates,
                "timeline": self._estimate_timeline(area, pattern),
                "special_considerations": self._get_special_considerations(substrate, pattern)
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced materials: {e}")
            return {"success": False, "error": str(e)}
    
    def get_technical_specifications(self, product_sku):
        """Get detailed technical specifications"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
                
            # Get product data
            products = self.db.search_products_by_sku(product_sku)
            if not products:
                return {"success": False, "error": f"Product {product_sku} not found"}
                
            product = products[0]
            
            # Extract technical data
            tech_specs = {
                "basic_specs": {
                    "sku": product.get('sku', ''),
                    "product_name": product.get('product_name', ''),
                    "material": product.get('material', ''),
                    "size": product.get('size', ''),
                    "thickness": product.get('thickness', ''),
                    "finish": product.get('finish', '')
                },
                "performance_specs": {
                    "dcof_rating": product.get('dcof_rating', ''),
                    "water_absorption": product.get('water_absorption', ''),
                    "breaking_strength": product.get('breaking_strength', ''),
                    "frost_resistance": product.get('frost_resistance', ''),
                    "chemical_resistance": product.get('chemical_resistance', '')
                },
                "installation_specs": {
                    "recommended_adhesive": self._get_recommended_adhesive(product),
                    "grout_joint_size": self._get_grout_joint_recommendations(product),
                    "substrate_requirements": self._get_substrate_requirements(product),
                    "temperature_range": "50-80°F (10-27°C)",
                    "humidity_requirements": "< 75% RH"
                }
            }
            
            return {
                "success": True,
                "product_sku": product_sku,
                "specifications": tech_specs,
                "compliance_codes": self._get_compliance_codes(product),
                "warranty_info": self._get_warranty_info(product)
            }
            
        except Exception as e:
            logger.error(f"Error getting technical specs: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_job_estimate(self, project_details):
        """Calculate comprehensive job estimate"""
        try:
            # Parse project details
            area = float(project_details.get('area', 0))
            complexity = project_details.get('complexity', 'standard')  # simple, standard, complex
            location = project_details.get('location', 'residential')   # residential, commercial
            timeline = project_details.get('timeline', 'standard')      # rush, standard, flexible
            
            # Base rates (example rates - would be configurable)
            base_rates = {
                "residential": {
                    "simple": 8.50,
                    "standard": 12.00,
                    "complex": 18.00
                },
                "commercial": {
                    "simple": 10.00,
                    "standard": 15.00,
                    "complex": 22.00
                }
            }
            
            base_rate = base_rates.get(location, base_rates["residential"]).get(complexity, 12.00)
            
            # Timeline multipliers
            timeline_multipliers = {
                "rush": 1.5,
                "standard": 1.0,
                "flexible": 0.9
            }
            
            multiplier = timeline_multipliers.get(timeline, 1.0)
            
            # Calculate estimates
            labor_cost = area * base_rate * multiplier
            
            # Material markup (contractor typically adds 20-30%)
            material_markup = 0.25
            
            # Overhead and profit (typically 15-25%)
            overhead_profit = 0.20
            
            subtotal = labor_cost * (1 + overhead_profit)
            
            return {
                "success": True,
                "area": area,
                "complexity": complexity,
                "location": location,
                "timeline": timeline,
                "rates": {
                    "base_rate_per_sq_ft": base_rate,
                    "timeline_multiplier": multiplier,
                    "material_markup": material_markup,
                    "overhead_profit": overhead_profit
                },
                "estimates": {
                    "labor_cost": round(labor_cost, 2),
                    "material_markup_percentage": int(material_markup * 100),
                    "subtotal": round(subtotal, 2),
                    "estimated_total_range": {
                        "low": round(subtotal * 0.9, 2),
                        "high": round(subtotal * 1.1, 2)
                    }
                },
                "timeline_estimate": self._estimate_installation_timeline(area, complexity),
                "crew_requirements": self._estimate_crew_requirements(area, complexity, timeline)
            }
            
        except Exception as e:
            logger.error(f"Error calculating job estimate: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_advanced_waste_factors(self, pattern, tile_size, substrate):
        """Calculate advanced waste factors"""
        base_waste = {
            "straight": 0.10,
            "diagonal": 0.15,
            "herringbone": 0.20,
            "complex": 0.25
        }
        
        # Size adjustments
        size_adjustments = {
            "large": -0.02,  # 24x24 and larger
            "standard": 0.0,  # 12x12 to 18x18
            "small": 0.03    # under 12x12
        }
        
        # Substrate adjustments
        substrate_adjustments = {
            "concrete": 0.0,
            "wood": 0.02,
            "existing_tile": 0.03,
            "uneven": 0.05
        }
        
        pattern_waste = base_waste.get(pattern, 0.10)
        size_adj = size_adjustments.get("standard", 0.0)  # Default to standard
        substrate_adj = substrate_adjustments.get(substrate, 0.0)
        
        total_waste = pattern_waste + size_adj + substrate_adj
        
        return {
            "pattern_waste": pattern_waste,
            "size_adjustment": size_adj,
            "substrate_adjustment": substrate_adj,
            "total_waste": total_waste
        }
    
    def _calculate_all_materials(self, area, total_area, tile_size, substrate, pattern):
        """Calculate comprehensive material list"""
        
        # Adhesive calculations
        adhesive_coverage = 40  # sq ft per bag (typical)
        adhesive_bags = math.ceil(total_area / adhesive_coverage)
        
        # Grout calculations  
        grout_coverage = 100  # sq ft per bag (typical for 1/8" joints)
        grout_bags = math.ceil(total_area / grout_coverage)
        
        # Additional materials
        materials = {
            "tiles": {
                "area_needed": total_area,
                "note": "Including waste factor"
            },
            "adhesive": {
                "bags_needed": adhesive_bags,
                "type": "Premium polymer-modified thinset",
                "coverage_per_bag": f"{adhesive_coverage} sq ft"
            },
            "grout": {
                "bags_needed": grout_bags,
                "type": "Polymer-modified sanded grout",
                "coverage_per_bag": f"{grout_coverage} sq ft"
            },
            "accessories": [
                {"item": "Tile spacers", "quantity": "1 set", "essential": True},
                {"item": "Leveling system", "quantity": "1 kit", "essential": True},
                {"item": "Grout sealer", "quantity": "1 quart", "essential": True},
                {"item": "Transition strips", "quantity": "As needed", "essential": False}
            ]
        }
        
        # Substrate-specific materials
        if substrate == "wood":
            materials["accessories"].extend([
                {"item": "Uncoupling membrane", "quantity": f"{int(total_area)} sq ft", "essential": True},
                {"item": "Membrane adhesive", "quantity": "2 bags", "essential": True}
            ])
        elif substrate == "concrete":
            materials["accessories"].append(
                {"item": "Primer/sealer", "quantity": "1 gallon", "essential": True}
            )
        
        return materials
    
    def _calculate_labor_estimates(self, area, pattern, substrate):
        """Calculate labor time estimates"""
        
        # Base installation rates (sq ft per day)
        base_rates = {
            "straight": 200,
            "diagonal": 150,
            "herringbone": 100,
            "complex": 80
        }
        
        # Substrate multipliers
        substrate_multipliers = {
            "concrete": 1.0,
            "wood": 0.8,
            "existing_tile": 0.7,
            "uneven": 0.6
        }
        
        daily_rate = base_rates.get(pattern, 150)
        substrate_mult = substrate_multipliers.get(substrate, 1.0)
        
        effective_rate = daily_rate * substrate_mult
        installation_days = area / effective_rate
        
        return {
            "installation_days": round(installation_days, 1),
            "preparation_days": round(installation_days * 0.3, 1),
            "finishing_days": round(installation_days * 0.2, 1),
            "total_days": round(installation_days * 1.5, 1),
            "daily_rate_sq_ft": effective_rate,
            "substrate_factor": substrate_mult
        }
    
    def _estimate_timeline(self, area, pattern):
        """Estimate project timeline"""
        complexity_days = {
            "straight": 1,
            "diagonal": 1.3,
            "herringbone": 1.8,
            "complex": 2.2
        }
        
        base_days = area / 200  # 200 sq ft per day baseline
        pattern_mult = complexity_days.get(pattern, 1.0)
        
        total_days = base_days * pattern_mult
        
        return {
            "preparation": "1 day",
            "installation": f"{math.ceil(total_days)} days",
            "finishing": "1 day",
            "total_project": f"{math.ceil(total_days) + 2} days"
        }
    
    def _get_special_considerations(self, substrate, pattern):
        """Get special installation considerations"""
        considerations = []
        
        if substrate == "wood":
            considerations.extend([
                "Install uncoupling membrane to prevent cracking",
                "Ensure subfloor deflection is within L/360 limits",
                "Check for squeaks and secure loose boards"
            ])
        elif substrate == "concrete":
            considerations.extend([
                "Test for moisture and pH levels",
                "Fill any cracks or level surface as needed",
                "Prime porous concrete surfaces"
            ])
        
        if pattern in ["herringbone", "complex"]:
            considerations.extend([
                "Create detailed layout plan before starting",
                "Use laser level for pattern alignment",
                "Allow extra time for cuts and adjustments"
            ])
        
        return considerations
    
    def _get_technical_specs(self, product_sku):
        """Get basic technical specifications"""
        # This would integrate with the database
        return {
            "water_absorption": "< 0.5%",
            "breaking_strength": "> 250 lbf",
            "dcof_rating": "0.42 (wet/dry)",
            "frost_resistance": "Yes",
            "recommended_applications": ["Floor", "Wall", "Commercial", "Residential"]
        }
    
    def _get_required_tools(self, product_sku):
        """Get required tools for installation"""
        return [
            {"tool": "Wet tile saw", "essential": True},
            {"tool": "Trowel (1/4\" x 3/8\" square notch)", "essential": True},
            {"tool": "Level (4-foot)", "essential": True},
            {"tool": "Rubber mallet", "essential": True},
            {"tool": "Tile spacers", "essential": True},
            {"tool": "Measuring tape", "essential": True},
            {"tool": "Chalk line", "essential": True},
            {"tool": "Grout float", "essential": True},
            {"tool": "Grout sponges", "essential": True},
            {"tool": "Safety glasses", "essential": True}
        ]
    
    def _get_preparation_steps(self, product_sku):
        """Get preparation steps"""
        return [
            "Ensure substrate is clean, dry, and level",
            "Check for structural soundness",
            "Apply primer if required",
            "Plan tile layout and mark center lines",
            "Acclimate tiles to room temperature",
            "Gather all tools and materials",
            "Install any required membranes",
            "Double-check measurements and square"
        ]
    
    def _get_recommended_adhesive(self, product):
        """Get recommended adhesive type"""
        material = product.get('material', '').lower()
        if 'porcelain' in material:
            return "Large-format polymer-modified thinset"
        elif 'natural stone' in material:
            return "Non-staining polymer-modified thinset"
        else:
            return "Standard polymer-modified thinset"
    
    def _get_grout_joint_recommendations(self, product):
        """Get grout joint size recommendations"""
        size = product.get('size', '')
        if '24' in size or '36' in size:
            return "1/8\" to 3/16\" minimum"
        elif '12' in size or '18' in size:
            return "1/16\" to 1/8\""
        else:
            return "1/16\" to 3/16\""
    
    def _get_substrate_requirements(self, product):
        """Get substrate requirements"""
        return [
            "Level within 1/4\" over 10 feet",
            "Structurally sound and rigid",
            "Clean and free of contaminants",
            "Properly cured (28 days for concrete)",
            "Within manufacturer's deflection limits"
        ]
    
    def _get_compliance_codes(self, product):
        """Get applicable building codes and standards"""
        return [
            "ANSI A137.1 - American National Standard Specifications for Ceramic Tile",
            "TCNA Handbook - Installation guidelines",
            "ADA Compliance - Slip resistance requirements",
            "Local building codes - Check jurisdiction requirements"
        ]
    
    def _get_warranty_info(self, product):
        """Get warranty information"""
        return {
            "manufacturer_warranty": "Limited lifetime warranty against manufacturing defects",
            "installation_warranty": "Contractor should provide installation warranty",
            "exclusions": "Normal wear, improper maintenance, substrate failure",
            "requirements": "Professional installation, approved materials"
        }
    
    def _estimate_installation_timeline(self, area, complexity):
        """Estimate installation timeline"""
        base_days = {
            "simple": area / 250,
            "standard": area / 200,
            "complex": area / 150
        }
        
        install_days = base_days.get(complexity, area / 200)
        
        return {
            "installation_only": f"{math.ceil(install_days)} days",
            "with_prep_and_finish": f"{math.ceil(install_days * 1.4)} days",
            "total_project": f"{math.ceil(install_days * 1.6)} days"
        }
    
    def _estimate_crew_requirements(self, area, complexity, timeline):
        """Estimate crew requirements"""
        if timeline == "rush":
            return {
                "lead_installer": 1,
                "assistants": 2,
                "total_crew": 3,
                "recommendation": "Larger crew for rush timeline"
            }
        elif area > 500:
            return {
                "lead_installer": 1,
                "assistants": 1,
                "total_crew": 2,
                "recommendation": "Two-person crew for large areas"
            }
        else:
            return {
                "lead_installer": 1,
                "assistants": 1 if complexity == "complex" else 0,
                "total_crew": 2 if complexity == "complex" else 1,
                "recommendation": "Standard crew size"
            }

@app.route('/')
def index():
    """Home page redirect to pro-chat"""
    return render_template('contractor_chat.html')

@app.route('/pro-chat')
def pro_chat():
    """Contractor chat interface"""
    return render_template('contractor_chat.html')

@app.route('/chat')
def chat():
    """Legacy chat route - redirect to pro-chat"""
    return render_template('contractor_chat.html')

@app.route('/api/chat', methods=['POST'])
def contractor_chat_api():
    """Contractor-focused chat endpoint with NEPQ scoring"""
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
            'mode': 'contractor',
            'aos_phase': result.get('aos_phase', 'discovery'),
            'requirements_complete': result.get('requirements_complete', False),
            'nepq_analysis': result.get('nepq_analysis', {}),
            'self_analysis': self_analysis
        })
        
    except Exception as e:
        logger.error(f"Error in contractor chat: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/installation/guide', methods=['POST'])
def get_installation_guide():
    """Get installation guide for a product"""
    try:
        data = request.get_json()
        product_sku = data.get('product_sku', '').strip()
        
        if not product_sku:
            return jsonify({'success': False, 'error': 'Product SKU is required'})
        
        agent = ContractorAgent(db_manager, rag_manager)
        result = agent.get_installation_guide(product_sku)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting installation guide: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/materials/advanced', methods=['POST'])
def calculate_advanced_materials():
    """Calculate advanced materials with contractor-specific details"""
    try:
        data = request.get_json()
        
        agent = ContractorAgent(db_manager, rag_manager)
        result = agent.calculate_advanced_materials(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error calculating advanced materials: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/specs/technical', methods=['POST'])
def get_technical_specs():
    """Get detailed technical specifications"""
    try:
        data = request.get_json()
        product_sku = data.get('product_sku', '').strip()
        
        if not product_sku:
            return jsonify({'success': False, 'error': 'Product SKU is required'})
        
        agent = ContractorAgent(db_manager, rag_manager)
        result = agent.get_technical_specifications(product_sku)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting technical specs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/estimate/job', methods=['POST'])
def calculate_job_estimate():
    """Calculate comprehensive job estimate"""
    try:
        data = request.get_json()
        
        agent = ContractorAgent(db_manager, rag_manager)
        result = agent.calculate_job_estimate(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error calculating job estimate: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/health')
def system_health():
    """System health check"""
    try:
        health_status = {
            'status': 'healthy',
            'mode': 'contractor',
            'port': 8083,
            'database': db_manager is not None,
            'rag': rag_manager is not None,
            'features': [
                'installation_guides',
                'technical_specifications',
                'advanced_material_calculations',
                'job_estimates',
                'timeline_planning',
                'crew_requirements'
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
    logger.info('Contractor client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Contractor client disconnected')

if __name__ == '__main__':
    logger.info("Starting Contractor Chat Application on port 8083")
    socketio.run(app, debug=True, host='0.0.0.0', port=8083)