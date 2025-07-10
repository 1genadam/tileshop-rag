#!/usr/bin/env python3
"""
Simple Tile Shop AI Agent - Natural LLM-based approach
Core Components: System Prompt + Message History + User Input + Tools
"""

import json
import logging
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import anthropic
from .aos_conversation_engine import AOSConversationEngine, ConversationContext
from .nepq_scoring_system import NEPQScoringSystem, ConversationAnalysis

logger = logging.getLogger(__name__)

def serialize_datetime(obj):
    """Custom JSON serializer for datetime and date objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class SimpleTileAgent:
    """Natural AI agent for tile shop assistance using proper LLM components"""
    
    def __init__(self, db_manager, rag_manager):
        self.db = db_manager
        self.rag = rag_manager
        self.client = anthropic.Anthropic()
        self.aos_engine = AOSConversationEngine()
        self.nepq_scorer = NEPQScoringSystem()
        
        # Core Component 1: System Prompt
        self.system_prompt = """You are Alex, a professional tile specialist at The Tile Shop. I help customers create beautiful tile installations and have helped hundreds of families find perfect solutions for their projects.

🔍 VISUAL TILE RECOGNITION CAPABILITIES:
You have access to advanced camera-based tile recognition. When customers mention having a tile, wanting to find similar tiles, or needing store locations, offer visual scanning:

VISUAL INTENT TRIGGERS - Offer camera scanning when customers say:
- "I have this tile..." / "I found this tile..."
- "Can you identify this tile?" / "What tile is this?"
- "Find similar tiles" / "Match this tile"
- "Where is this tile in the store?" / "Do you have this in stock?"
- "I'm looking at tiles in your showroom"

VISION WORKFLOW:
1. Detect visual intent from customer message
2. Offer: "I can help you scan that tile with your camera! Would you like to:"
   - 🔍 "Find Similar Tiles" (match against our database)
   - 📍 "Find in Store" (get aisle location and inventory)
3. If accepted, trigger vision scanning mode
4. Process results and continue conversation naturally

IMPORTANT: Always offer camera scanning when visual intent is detected. This significantly improves customer experience and sales conversion.

🎯 ENHANCED AOS-NEPQ HYBRID METHODOLOGY - TARGET: 5/5 ON EVERY STEP
(Combining proven AOS structure with NEPQ emotional engagement techniques)

CONVERSATION APPROACH - ANSWER FIRST, THEN QUALIFY:

1️⃣ NATURAL GREETING & IMMEDIATE HELP (Target: 5/5):
- Warmly introduce yourself: "Hi! I'm Alex from The Tile Shop"
- ANSWER CUSTOMER QUESTIONS FIRST before qualifying
- If they ask "do you have floor tile?" → "Absolutely! We have hundreds of floor tile options..."
- THEN naturally get their name and build rapport
- Build credibility through helpfulness, not scripts

2️⃣ NATURAL NEEDS DISCOVERY - CONVERSATIONAL APPROACH (Target: 7/7):
GATHER THESE KEY DETAILS through natural conversation (not rigid questioning):

ESSENTIAL INFORMATION TO COLLECT:
- Room type and approximate dimensions
- Current situation and what's not working  
- Style preferences and desired outcome
- Installation method (DIY vs contractor)
- Timeline for the project
- Budget range and investment readiness
- Understanding consequences of delay

CONVERSATIONAL FLOW EXAMPLES:
- "What room are you tiling?" (natural vs "Question 1/7")
- "What's your space like - roughly how big?" (natural vs demanding exact measurements)
- "What's driving this project? Any issues with current flooring?" (natural problem discovery)

FLEXIBILITY: You can help with product searches and basic questions even before getting all details. 
PRIORITY: Answer customer questions immediately, then naturally gather more information.

NATURAL CONVERSATION FLOW:
1. Answer customer's immediate question/need
2. Naturally gather information through helpful conversation
3. When you have enough details, proceed with product recommendations
4. Use tools as needed to help customer (search_products, calculate_project_requirements)

🎯 BE HELPFUL FIRST: If customer asks "do you have X?" → Answer "Yes! We have..." then naturally discover their needs

🎯 NEPQ INTEGRATION: Use emotional discovery and problem awareness naturally within conversation.

TOOL USAGE: Use search_products and calculate_project_requirements when helpful, not when arbitrary question count is met.

3️⃣ PRODUCT RECOMMENDATIONS - HELPFUL GUIDANCE (Target: 7/7):
WHEN YOU HAVE SUFFICIENT INFORMATION:
1. Use search_products to find great tile options for their needs
2. Use calculate_project_requirements when you have room dimensions  
3. Present options with benefits that address their specific situation
4. Guide toward next steps when appropriate

NATURAL TRANSITION:
"Based on what you've told me about [their situation], let me show you some great options that would work well..."

FLEXIBLE APPROACH:
- Help with product searches even with partial information
- Calculate quantities when you have dimensions
- Build understanding progressively through conversation
- Use attempt_close when customer shows buying interest

TOOL SEQUENCING: Use tools when helpful for the customer, not based on rigid question counts.

4️⃣ NATURAL CLOSING - COMMITMENT WHEN APPROPRIATE (Target: 7/7):
WHEN CUSTOMER SHOWS BUYING INTEREST:
- "Do you feel like this could work for your project?"
- "What appeals to you most about this option?"
- "Would you like me to calculate exactly what you'll need?"
- "Should we get your order started today?"
- Create helpful urgency: "I can have these ready for pickup this weekend"
- Focus on solving their specific problems and needs

5️⃣ OBJECTION HANDLING - NEPQ FACTS VS MEANINGS FRAMEWORK (Target: 5/5):
ENHANCED OBJECTION HANDLING using NEPQ methodology:
1. CLARIFY: Separate fact from meaning - "Help me understand what specifically concerns you about [objection]?"
2. DEFAME: Cast doubt on current frame - "Have you considered that [alternative perspective]?"
3. REFRAME: Introduce new frame aligned with their goals
4. EMPATHIZE: "I completely understand - this is an important decision"  
5. RE-ASK: "If [reframe addresses concern], can we move forward with this?"

NEPQ OBJECTION EXAMPLES:
- "It's too expensive" = MEANING, not fact
- CLARIFY: "When you say expensive, what are you comparing it to?"
- DEFAME: "What's the cost of not solving this flooring problem?"
- REFRAME: "Investment in solving your problem vs. ongoing frustration"

🛑 ABSOLUTELY FORBIDDEN ACTIONS:
- Using search_products before collecting ALL 7 questions (including NEPQ problem awareness and consequences)
- Skipping any of the seven mandatory questions  
- Providing product recommendations without understanding their problems
- Generic responses like "How can I assist you today?"
- Failing to attempt a close with NEPQ commitment questions

✅ MANDATORY REQUIREMENTS CHECKLIST:
Before using search_products tool, you MUST have:
- Customer name ✓
- Room type & exact dimensions (length × width) ✓
- NEPQ Problem awareness (current state issues) ✓ 
- Style preferences & solution awareness ✓
- Installation method ✓
- Timeline ✓
- NEPQ Consequence questions (cost of inaction) ✓
- Budget range & investment readiness ✓

🎯 ENHANCED PROFESSIONAL LANGUAGE EXAMPLES:
Opening: "Hi! I'm Alex from The Tile Shop. May I have your name?"
Status Frame: "This conversation is really just for me to understand what you're dealing with now versus what you're hoping to achieve, to see if there's even a gap worth addressing. Toward the end, if it seems like we might be able to help, we can talk about possible next steps. Would that help you?"
Question 1/7: "What type of room are you working on? And most importantly, what are the exact measurements (length and width) of the area you're planning to tile?"
Question 2/7: "So to me, it sounds like your current flooring situation is going 100% perfect for you. Is there anything you would change about your current flooring if you could?"
Precision Probing: "Tell me more... about that?" "In what way, though?" "How long has that been going on?"
Question 3/7: "Now that I understand what's not working, what would your ideal tile situation look like? Do you have any specific style or color preferences in mind?"
Question 4/7: "Will you be installing this yourself or working with a contractor?"
Question 5/7: "When are you hoping to start this project?"
Question 6/7: "What happens if you don't do anything about this flooring issue and it continues for another 6-12 months? Have you thought about what that might cost you?"
Question 7/7: "What's your budget range for this project? And how important is it for you to solve this now rather than later?"
NEPQ Transition: "Based on what you've told me about [specific problem], and your desire for [ideal outcome], let me show you how we can solve this..."
NEPQ Close: "Do you feel like this could be the answer for you?" "What specific parts will help you most?" "Why do you feel it would help, though?"
Final Close: "Based on everything we've discussed, should we go ahead and get your order placed today?"

When customers ask about installation help:
1. IMPORTANT: If you see a phone number anywhere in the user's message (like "My phone number is: 847-302-2594"), immediately use the lookup_customer tool to verify their purchase history
2. If they mention a specific product but don't provide a phone number, ask for their phone number to look up their purchase history  
3. After using lookup_customer, provide specific installation guidance for their verified purchase
4. Recommend installation accessories: thinset, grout, sealer, sponges, trowels, wedges, leveling system, silicone, buckets, float

CONVERSATION STORAGE: Always mention that you want to store the conversation: "I'd like to store our conversation for future context so you're not starting over the next time we chat. What phone number would you like this saved under?"

Be conversational and knowledgeable - like a trusted tile expert who's helping them create their dream space. Ask intelligent follow-up questions that move the sale forward."""

    def lookup_customer(self, phone_number: str) -> Dict[str, Any]:
        """Tool: Look up customer and their purchase history"""
        try:
            # Get customer info
            customer = self.db.get_or_create_customer(phone_number)
            if not customer:
                return {"found": False, "message": "Customer not found"}
            
            # Get their purchase history
            purchases = self.db.get_customer_purchases(customer['customer_id'])
            
            return {
                "found": True,
                "customer": customer,
                "purchases": purchases,
                "message": f"Found {len(purchases)} purchases for {customer.get('first_name', 'customer')}"
            }
        except Exception as e:
            logger.error(f"Error looking up customer: {e}")
            return {"found": False, "error": str(e)}

    def search_products(self, query: str) -> Dict[str, Any]:
        """Tool: Search for products using RAG system"""
        try:
            result = self.rag.enhanced_chat(query, "agent_search")
            return {
                "success": True,
                "response": result.get('response', ''),
                "products": result.get('products', [])
            }
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {"success": False, "error": str(e)}

    def get_installation_guide(self, product_name: str) -> Dict[str, Any]:
        """Tool: Get installation guidance for a specific product"""
        try:
            query = f"installation instructions for {product_name}"
            result = self.rag.enhanced_chat(query, "installation_guide")
            return {
                "success": True,
                "guidance": result.get('response', ''),
                "product": product_name
            }
        except Exception as e:
            logger.error(f"Error getting installation guide: {e}")
            return {"success": False, "error": str(e)}

    def get_aos_questions(self, project_type: str = "", customer_phase: str = "discovery", gathered_info: str = "{}", conversation_history: str = "") -> Dict[str, Any]:
        """Tool: Get intelligent AOS questions based on conversation context"""
        try:
            # Parse gathered info
            try:
                info_dict = json.loads(gathered_info) if gathered_info else {}
            except json.JSONDecodeError:
                info_dict = {}
            
            # Extract information from conversation history
            if conversation_history:
                extracted_info = self.aos_engine.extract_info_from_response(conversation_history, None)
                info_dict.update(extracted_info)
            
            # Create conversation context
            context = ConversationContext(
                project_type=project_type.lower(),
                customer_phase=customer_phase,
                gathered_info=info_dict
            )
            
            # Get next best questions (limit to 1-2 max)
            questions = self.aos_engine.get_next_questions(context, num_questions=1)
            
            # Check if we should advance phase
            next_phase = self.aos_engine.advance_conversation_phase(context)
            
            return {
                "success": True,
                "questions": questions,
                "current_phase": customer_phase,
                "next_phase": next_phase,
                "phase_changed": next_phase != customer_phase,
                "conversation_tips": self._get_conversation_tips(context),
                "extracted_info": info_dict
            }
        except Exception as e:
            logger.error(f"Error getting AOS questions: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_conversation_tips(self, context: ConversationContext) -> List[str]:
        """Get conversation tips based on current context"""
        tips = []
        
        if not context.phone_number:
            tips.append("Prioritize getting phone number for follow-up")
        
        if context.customer_phase == "discovery":
            tips.append("Focus on understanding their project vision")
        elif context.customer_phase == "qualification":
            tips.append("Assess timeline, budget, and decision-making process")
        elif context.customer_phase == "recommendation":
            tips.append("Present tailored solutions based on their needs")
        elif context.customer_phase == "closing":
            tips.append("Create urgency and guide toward next steps")
        
        return tips

    def save_customer_project(self, phone_number: str, project_info: str) -> Dict[str, Any]:
        """Tool: Save customer project information for future reference"""
        try:
            # Get or create customer
            customer = self.db.get_or_create_customer(phone_number)
            if not customer:
                return {"success": False, "message": "Could not create customer record"}
            
            # For now, we'll add this to the customer notes
            # In the future, this could be a separate project_conversations table
            current_notes = customer.get('notes', '') or ''
            updated_notes = f"{current_notes}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {project_info}".strip()
            
            # Update customer notes (simplified approach for now)
            # In production, this would update the database
            return {
                "success": True,
                "message": f"Project information saved for {customer.get('first_name', 'customer')}",
                "customer_id": customer.get('customer_id'),
                "project_info": project_info
            }
        except Exception as e:
            logger.error(f"Error saving customer project: {e}")
            return {"success": False, "error": str(e)}

    def validate_aos_requirements(self, conversation_history: List[Dict], intended_action: str) -> Dict[str, Any]:
        """Validate that mandatory AOS requirements are met before proceeding"""
        
        # Extract conversation data to check requirements
        conversation_text = ""
        for msg in conversation_history:
            if msg.get("role") == "user":
                conversation_text += f" {msg.get('content', '')}"
        
        conversation_text = conversation_text.lower()
        
        # Debug logging
        logger.info(f"AOS Validation - Action: {intended_action}")
        logger.info(f"AOS Validation - Conversation text: {conversation_text}")
        logger.info(f"AOS Validation - Full history: {conversation_history}")
        
        # Check mandatory requirements (Enhanced AOS-NEPQ)
        requirements_met = {
            "customer_name": self._check_name_collected(conversation_text),
            "room_and_dimensions": self._check_dimensions_collected(conversation_text),
            "problem_awareness": self._check_problem_awareness_collected(conversation_text),
            "style_preferences": self._check_style_preferences_collected(conversation_text),
            "installation_method": self._check_installation_method_collected(conversation_text),
            "timeline": self._check_timeline_collected(conversation_text),
            "consequence_questions": self._check_consequence_questions_collected(conversation_text),
            "budget": self._check_budget_collected(conversation_text)
        }
        
        # Check if products have been searched in this conversation
        product_search_completed = self._check_product_search_completed(conversation_history)
        
        # Determine if action can proceed (Enhanced AOS-NEPQ)
        if intended_action == "search_products":
            critical_requirements = ["customer_name", "room_and_dimensions", "problem_awareness", "style_preferences", "installation_method", "timeline", "consequence_questions", "budget"]
            missing_critical = [req for req in critical_requirements if not requirements_met[req]]
            
            if missing_critical:
                return {
                    "can_proceed": False,
                    "blocking_error": True,
                    "missing_requirements": missing_critical,
                    "message": f"Cannot search products until {', '.join(missing_critical)} collected"
                }
        
        if intended_action == "calculate_project_requirements":
            # Block calculations until all 7 questions are answered AND products have been searched
            calculation_requirements = ["customer_name", "room_and_dimensions", "problem_awareness", "style_preferences", "installation_method", "timeline", "consequence_questions", "budget"]
            missing_calc = [req for req in calculation_requirements if not requirements_met[req]]
            
            if missing_calc:
                return {
                    "can_proceed": False,
                    "blocking_error": True,
                    "missing_requirements": missing_calc,
                    "message": f"Cannot calculate requirements until {', '.join(missing_calc)} collected"
                }
            
            # Additional check: Enforce mandatory sequence - products BEFORE calculations
            # This ensures proper AOS flow: search_products → calculate_project_requirements → attempt_close
            if not product_search_completed:
                return {
                    "can_proceed": False,
                    "blocking_error": True,
                    "missing_requirements": ["product_search_first"],
                    "message": "Must search products before calculating requirements - follow AOS sequence"
                }
        
        return {
            "can_proceed": True,
            "blocking_error": False,
            "requirements_met": requirements_met,
            "message": "Requirements satisfied"
        }
    
    def _check_name_collected(self, conversation_text: str) -> bool:
        """Check if customer name has been collected"""
        name_indicators = ["my name is", "i'm", "call me", "this is"]
        return any(indicator in conversation_text for indicator in name_indicators)
    
    def _check_dimensions_collected(self, conversation_text: str) -> bool:
        """Check if dimensions have been collected"""
        import re
        # Look for dimension patterns like "8x10", "8 by 10", "8 feet by 10 feet", "80 square feet"
        dimension_patterns = [
            r'\d+\s*[x×]\s*\d+',
            r'\d+\s*by\s*\d+',
            r'\d+\s*feet?\s*by\s*\d+\s*feet?',
            r'\d+\s*sq\s*ft',
            r'\d+\s*square\s*feet?'
        ]
        return any(re.search(pattern, conversation_text) for pattern in dimension_patterns)
    
    def _check_problem_awareness_collected(self, conversation_text: str) -> bool:
        """Check if NEPQ problem awareness questions have been asked/answered"""
        problem_indicators = ["change about", "not working", "problem", "issue", "bothering", "frustrating", "difficult", "challenge", "wrong with", "hate about", "annoying", "ugly", "old", "worn", "damaged", "cracked"]
        return any(indicator in conversation_text for indicator in problem_indicators)
    
    def _check_consequence_questions_collected(self, conversation_text: str) -> bool:
        """Check if NEPQ consequence questions have been asked (cost of inaction)"""
        consequence_indicators = ["if you don't", "what happens if", "cost of not", "continue for", "gets worse", "another year", "impact", "consequence", "important to solve"]
        return any(indicator in conversation_text for indicator in consequence_indicators)
    
    def _check_style_preferences_collected(self, conversation_text: str) -> bool:
        """Check if style preferences have been collected"""
        style_indicators = ["modern", "traditional", "rustic", "contemporary", "color", "style", "prefer", "like", "want", "gray", "white", "black", "brown", "beige", "blue", "green", "ideal"]
        return any(indicator in conversation_text for indicator in style_indicators)
    
    def _check_budget_collected(self, conversation_text: str) -> bool:
        """Check if budget information has been collected"""
        budget_indicators = ["budget", "$", "dollars", "cost", "price", "spend", "around", "1000", "500", "1500", "2000", "investment", "important to solve"]
        return any(indicator in conversation_text for indicator in budget_indicators)
    
    def _check_installation_method_collected(self, conversation_text: str) -> bool:
        """Check if installation method has been discussed"""
        installation_indicators = ["contractor", "diy", "myself", "professional", "install"]
        return any(indicator in conversation_text for indicator in installation_indicators)
    
    def _check_timeline_collected(self, conversation_text: str) -> bool:
        """Check if timeline has been discussed"""
        timeline_indicators = ["start", "begin", "timeline", "when", "next week", "month", "soon"]
        return any(indicator in conversation_text for indicator in timeline_indicators)
    
    def _check_product_search_completed(self, conversation_history: List[Dict]) -> bool:
        """Check if products have been searched in this conversation"""
        # Look for assistant messages that contain product search results
        for msg in conversation_history:
            if msg.get("role") == "assistant":
                content = msg.get("content", "").lower()
                # Check for product search indicators in assistant responses
                search_indicators = [
                    "here are some great options",
                    "i found these",
                    "these tiles would be perfect",
                    "sku",
                    "product name",
                    "per square foot",
                    "tile options",
                    "recommendations"
                ]
                if any(indicator in content for indicator in search_indicators):
                    return True
        return False

    def calculate_project_requirements(self, dimensions: str, tile_size: str = "12x12", tile_price: float = 4.99, pattern: str = "straight") -> Dict[str, Any]:
        """Tool: Calculate professional project requirements with waste factors"""
        try:
            import re
            
            # Parse dimensions
            dimension_match = re.search(r'(\d+\.?\d*)\s*[x×by]\s*(\d+\.?\d*)', dimensions.lower())
            if not dimension_match:
                return {"success": False, "error": "Could not parse dimensions. Please provide in format '8x10' or '8 by 10'"}
            
            length = float(dimension_match.group(1))
            width = float(dimension_match.group(2))
            base_sq_ft = length * width
            
            # Determine waste factor based on pattern complexity
            waste_factors = {
                "straight": 0.10,      # 10% for straight lay, brick pattern
                "diagonal": 0.15,      # 15% for diagonal
                "herringbone": 0.20,   # 20% for herringbone, basket weave
                "complex": 0.20        # 20% for very complex patterns
            }
            
            waste_factor = waste_factors.get(pattern, 0.10)
            total_sq_ft = base_sq_ft * (1 + waste_factor)
            
            # Calculate box requirements (assume 10 sq ft per box typical)
            sq_ft_per_box = 10.0
            boxes_needed = math.ceil(total_sq_ft / sq_ft_per_box)
            total_coverage = boxes_needed * sq_ft_per_box
            
            # Calculate costs
            tile_cost = total_sq_ft * tile_price
            
            # Essential materials costs
            materials = {
                "premium_thinset": {"quantity": max(1, math.ceil(total_sq_ft / 50)), "unit_price": 35.00},
                "grout": {"quantity": max(1, math.ceil(total_sq_ft / 100)), "unit_price": 32.00},
                "grout_sealer": {"quantity": 1, "unit_price": 28.00},
                "tile_spacers": {"quantity": 1, "unit_price": 18.00},
                "leveling_system": {"quantity": 1, "unit_price": 45.00}
            }
            
            materials_cost = sum(item["quantity"] * item["unit_price"] for item in materials.values())
            total_project_cost = tile_cost + materials_cost
            
            return {
                "success": True,
                "dimensions": f"{length} x {width} feet",
                "base_square_footage": round(base_sq_ft, 1),
                "waste_factor_percent": int(waste_factor * 100),
                "total_square_footage_needed": round(total_sq_ft, 1),
                "boxes_needed": boxes_needed,
                "total_coverage": round(total_coverage, 1),
                "tile_price_per_sq_ft": tile_price,
                "tile_cost": round(tile_cost, 2),
                "materials_breakdown": materials,
                "materials_cost": round(materials_cost, 2),
                "total_project_cost": round(total_project_cost, 2),
                "pattern_type": pattern
            }
            
        except Exception as e:
            logger.error(f"Error calculating project requirements: {e}")
            return {"success": False, "error": str(e)}

    def attempt_close(self, project_summary: str, timeline: str = "soon", urgency_reason: str = "availability") -> Dict[str, Any]:
        """Tool: Attempt to close the sale with professional techniques"""
        try:
            closing_techniques = {
                "direct": f"Should we go ahead and get your order placed today?",
                "assumed": f"I'll get these materials ready for you. When would you like to pick them up?",
                "urgency": f"I can reserve these tiles for you while you finalize your decision. These are popular and I'd recommend securing your quantity soon.",
                "alternative": f"Would you prefer pickup or delivery for your {timeline} start date?"
            }
            
            # Create urgency based on timeline
            urgency_messages = {
                "soon": "Since you're starting soon, I can have everything ready this week.",
                "next week": "Perfect timing - I can have all materials ready for your contractor by early next week.",
                "this week": "Excellent! I can expedite this order to have everything ready in just a few days."
            }
            
            urgency_message = urgency_messages.get(timeline.lower(), "I can coordinate the timing to match your project schedule.")
            
            return {
                "success": True,
                "direct_close": closing_techniques["direct"],
                "assumed_close": closing_techniques["assumed"],
                "urgency_close": closing_techniques["urgency"],
                "urgency_message": urgency_message,
                "next_steps": [
                    "Finalize quantities and selections",
                    "Arrange pickup or delivery timing",
                    "Coordinate with contractor if applicable",
                    "Process payment and order"
                ],
                "project_summary": project_summary
            }
        except Exception as e:
            logger.error(f"Error in close attempt: {e}")
            return {"success": False, "error": str(e)}

    def get_installation_accessories(self, product_type: str = None) -> List[Dict[str, Any]]:
        """Tool: Get recommended installation accessories"""
        base_accessories = [
            {"item": "Thinset Adhesive", "purpose": "Bonds tile to substrate", "essential": True},
            {"item": "Grout", "purpose": "Fills joints between tiles", "essential": True},
            {"item": "1/4\" Notched Trowel", "purpose": "Applies adhesive evenly", "essential": True},
            {"item": "Tile Leveling System", "purpose": "Prevents lippage", "essential": True},
            {"item": "Grout Float", "purpose": "Applies grout smoothly", "essential": True},
            {"item": "Grout Sponges", "purpose": "Cleans excess grout", "essential": True},
            {"item": "Tile Sealer", "purpose": "Protects grout and tile", "essential": False},
            {"item": "Silicone Caulk", "purpose": "Seals edges and corners", "essential": True},
            {"item": "Mixing Bucket", "purpose": "Mixes adhesive and grout", "essential": True},
            {"item": "Tile Spacers/Wedges", "purpose": "Maintains consistent spacing", "essential": True}
        ]
        
        # Add product-specific accessories
        if product_type and "anti-fracture" in product_type.lower():
            base_accessories.append({
                "item": "1/2\" Notched Trowel", 
                "purpose": "For tile installation over anti-fracture mat", 
                "essential": True
            })
        
        return base_accessories

    def process_customer_query(self, query: str, conversation_history: List[Dict] = None, customer_phone: str = None, customer_name: str = None) -> Dict[str, Any]:
        """Process customer query with enhanced AOS tracking"""
        try:
            # Enhanced conversation history with customer info
            if conversation_history is None:
                conversation_history = []
            
            # Build conversation for AOS tracking
            conversation_text = ""
            for msg in conversation_history:
                if msg.get("role") == "user":
                    conversation_text += f" {msg.get('content', '')}"
            conversation_text += f" {query}"
            
            # Check current Enhanced AOS-NEPQ phase progress
            requirements_met = {
                "customer_name": self._check_name_collected(conversation_text) or bool(customer_name),
                "room_and_dimensions": self._check_dimensions_collected(conversation_text),
                "problem_awareness": self._check_problem_awareness_collected(conversation_text),
                "style_preferences": self._check_style_preferences_collected(conversation_text),
                "installation_method": self._check_installation_method_collected(conversation_text),
                "timeline": self._check_timeline_collected(conversation_text),
                "consequence_questions": self._check_consequence_questions_collected(conversation_text),
                "budget": self._check_budget_collected(conversation_text)
            }
            
            # Determine AOS phase
            total_requirements = len(requirements_met)
            completed_requirements = sum(requirements_met.values())
            
            if completed_requirements == 0:
                aos_phase = "greeting"
            elif completed_requirements < total_requirements:
                aos_phase = "needs_assessment"
            else:
                aos_phase = "design_and_details"
            
            # Process with standard chat method
            result = self.chat(query, conversation_history, customer_phone)
            
            # Enhance result with AOS tracking
            result.update({
                "aos_phase": aos_phase,
                "requirements_complete": completed_requirements == total_requirements,
                "progress": f"{completed_requirements}/{total_requirements}",
                "next_question_number": completed_requirements + 1 if completed_requirements < total_requirements else None
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing customer query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm experiencing some technical difficulties. Please try again."
            }

    def chat(self, message: str, conversation_history: List[Dict] = None, phone_number: str = None) -> Dict[str, Any]:
        """Main chat method - Core Component Integration"""
        try:
            # Core Component 2: Message History
            if conversation_history is None:
                conversation_history = []
            
            # Core Component 3: User Input
            user_message = message.strip()
            
            # If phone number is provided, enhance the user message
            if phone_number:
                user_message += f"\n\nMy phone number is: {phone_number}"
            
            # Build conversation for Claude
            messages = []
            
            # Add conversation history
            for turn in conversation_history:
                if turn.get('role') == 'user':
                    messages.append({"role": "user", "content": turn['content']})
                elif turn.get('role') == 'assistant':
                    messages.append({"role": "assistant", "content": turn['content']})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Core Component 4: Tools Definition
            tools = [
                {
                    "name": "lookup_customer",
                    "description": "Look up a customer by phone number to see their purchase history",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "phone_number": {"type": "string", "description": "Customer's phone number"}
                        },
                        "required": ["phone_number"]
                    }
                },
                {
                    "name": "search_products",
                    "description": "Search for tiles and products in our inventory",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for products"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_installation_guide",
                    "description": "Get detailed installation instructions for a specific product",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string", "description": "Name of the product to get installation guide for"}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "get_installation_accessories", 
                    "description": "Get list of recommended installation accessories and tools",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "product_type": {"type": "string", "description": "Type of product being installed (optional)"}
                        }
                    }
                },
                {
                    "name": "get_aos_questions",
                    "description": "Get intelligent AOS questions based on conversation context and learning data",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "project_type": {"type": "string", "description": "Type of project (kitchen, bathroom, etc.)"},
                            "customer_phase": {"type": "string", "description": "Current conversation phase: discovery, qualification, recommendation, closing"},
                            "gathered_info": {"type": "string", "description": "JSON string of information already gathered about customer"},
                            "conversation_history": {"type": "string", "description": "Recent conversation messages to extract context from"}
                        }
                    }
                },
                {
                    "name": "save_customer_project",
                    "description": "Save customer project information for future reference",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "phone_number": {"type": "string", "description": "Customer's phone number"},
                            "project_info": {"type": "string", "description": "Project details and conversation notes"}
                        },
                        "required": ["phone_number", "project_info"]
                    }
                },
                {
                    "name": "calculate_project_requirements",
                    "description": "Calculate professional project requirements including quantities, waste factors, and total costs",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "dimensions": {"type": "string", "description": "Room dimensions (e.g., '8x10' or '8 by 10')"},
                            "tile_size": {"type": "string", "description": "Tile size (optional, defaults to 12x12)"},
                            "tile_price": {"type": "number", "description": "Price per square foot (optional, defaults to 4.99)"},
                            "pattern": {"type": "string", "description": "Installation pattern: straight, diagonal, herringbone, complex (optional, defaults to straight)"}
                        },
                        "required": ["dimensions"]
                    }
                },
                {
                    "name": "attempt_close",
                    "description": "Attempt to close the sale with professional techniques after presenting products and calculations",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "project_summary": {"type": "string", "description": "Brief summary of the project and recommendations"},
                            "timeline": {"type": "string", "description": "Customer's project timeline (optional)"},
                            "urgency_reason": {"type": "string", "description": "Reason for urgency (optional)"}
                        },
                        "required": ["project_summary"]
                    }
                }
            ]
            
            # Core Component 5: LLM Processing with Tools
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                system=self.system_prompt,
                messages=messages,
                tools=tools
            )
            
            # Handle tool calls
            assistant_response = ""
            tool_results = []
            
            for content in response.content:
                if content.type == "text":
                    assistant_response += content.text
                elif content.type == "tool_use":
                    # Execute the tool
                    tool_name = content.name
                    tool_input = content.input
                    
                    if tool_name == "lookup_customer":
                        result = self.lookup_customer(tool_input["phone_number"])
                        tool_results.append({"tool": tool_name, "result": result})
                        
                        # Continue conversation with tool result
                        messages.append({"role": "assistant", "content": response.content})
                        messages.append({
                            "role": "user", 
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": json.dumps(result, default=serialize_datetime)  # Handle datetime serialization
                                }
                            ]
                        })
                        
                        # Get follow-up response
                        follow_up = self.client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1500,
                            system=self.system_prompt,
                            messages=messages,
                            tools=tools
                        )
                        
                        for follow_content in follow_up.content:
                            if follow_content.type == "text":
                                assistant_response += follow_content.text
                    
                    elif tool_name == "search_products":
                        # Validate AOS requirements before product search
                        validation = self.validate_aos_requirements(messages, "search_products")
                        
                        if not validation["can_proceed"]:
                            # Block product search and guide back to requirements collection (Enhanced AOS-NEPQ)
                            missing = validation["missing_requirements"]
                            
                            if "customer_name" in missing:
                                assistant_response += "\n\nBefore I can show you the perfect tile options, may I have your name?"
                            elif "room_and_dimensions" in missing:
                                assistant_response += "\n\n**Question 1 of 7:** What type of room are you working on? And most importantly, what are the exact measurements (length and width) of the area you're planning to tile?"
                            elif "problem_awareness" in missing:
                                assistant_response += "\n\n**Question 2 of 7:** So to me, it sounds like your current flooring situation is going 100% perfect for you. Is there anything you would change about your current flooring if you could?"
                            elif "style_preferences" in missing:
                                assistant_response += "\n\n**Question 3 of 7:** Now that I understand what's not working, what would your ideal tile situation look like? Do you have any specific style or color preferences in mind?"
                            elif "installation_method" in missing:
                                assistant_response += "\n\n**Question 4 of 7:** Will you be installing this yourself or working with a contractor?"
                            elif "timeline" in missing:
                                assistant_response += "\n\n**Question 5 of 7:** When are you hoping to start this project?"
                            elif "consequence_questions" in missing:
                                assistant_response += "\n\n**Question 6 of 7:** What happens if you don't do anything about this flooring issue and it continues for another 6-12 months? Have you thought about what that might cost you?"
                            elif "budget" in missing:
                                assistant_response += "\n\n**Question 7 of 7:** What's your budget range for this project? And how important is it for you to solve this now rather than later?"
                            
                            # Add validation result to tool results for tracking
                            tool_results.append({
                                "tool": "validation_check", 
                                "result": validation,
                                "blocked_action": "search_products"
                            })
                        else:
                            # Requirements met - proceed with product search
                            result = self.search_products(tool_input["query"])
                            tool_results.append({"tool": tool_name, "result": result})
                            assistant_response += f"\n\n{result.get('response', '')}"
                            
                            # AUTO-SEQUENCE: After successful product search, automatically proceed to calculations and close
                            if result.get('success', True):  # If product search was successful
                                try:
                                    # Extract dimensions from conversation for calculations
                                    conversation_text = ""
                                    for msg in messages:
                                        if msg.get("role") == "user":
                                            conversation_text += f" {msg.get('content', '')}"
                                    
                                    dimensions_match = None
                                    import re
                                    dimension_patterns = [
                                        r'(\d+)\s*[x×by]\s*(\d+)',
                                        r'(\d+)\s*feet?\s*by\s*(\d+)\s*feet?'
                                    ]
                                    for pattern in dimension_patterns:
                                        match = re.search(pattern, conversation_text.lower())
                                        if match:
                                            dimensions_match = f"{match.group(1)}x{match.group(2)}"
                                            break
                                    
                                    if dimensions_match:
                                        # AUTO-CALCULATE: Perform project calculations 
                                        calc_result = self.calculate_project_requirements(dimensions_match)
                                        tool_results.append({"tool": "calculate_project_requirements", "result": calc_result})
                                        if calc_result.get('success', True):
                                            assistant_response += f"\n\n**PROJECT CALCULATIONS:**\n{calc_result.get('summary', '')}"
                                            
                                            # AUTO-CLOSE: Attempt to close the sale
                                            project_summary = f"Kitchen floor project: {dimensions_match}, {calc_result.get('total_sq_ft', 'TBD')} sq ft total"
                                            close_result = self.attempt_close(project_summary, "next week", "availability")
                                            tool_results.append({"tool": "attempt_close", "result": close_result})
                                            assistant_response += f"\n\n{close_result.get('message', '')}"
                                        
                                except Exception as e:
                                    logger.error(f"Error in AOS auto-sequence: {e}")
                                    # Continue without failing the whole response
                    
                    elif tool_name == "get_installation_guide":
                        result = self.get_installation_guide(tool_input["product_name"])
                        tool_results.append({"tool": tool_name, "result": result})
                        assistant_response += f"\n\n{result.get('guidance', '')}"
                    
                    elif tool_name == "get_installation_accessories":
                        result = self.get_installation_accessories(tool_input.get("product_type"))
                        tool_results.append({"tool": tool_name, "result": result})
                        
                        # Format accessories nicely
                        essential = [acc for acc in result if acc.get("essential")]
                        optional = [acc for acc in result if not acc.get("essential")]
                        
                        accessories_text = "\n\n**Essential Installation Accessories:**\n"
                        for acc in essential:
                            accessories_text += f"• **{acc['item']}** - {acc['purpose']}\n"
                        
                        if optional:
                            accessories_text += "\n**Optional but Recommended:**\n"
                            for acc in optional:
                                accessories_text += f"• **{acc['item']}** - {acc['purpose']}\n"
                        
                        assistant_response += accessories_text
                    
                    elif tool_name == "get_aos_questions":
                        # Build conversation history string for context extraction
                        history_text = ""
                        for msg in messages:
                            if msg["role"] == "user":
                                history_text += f"Customer: {msg['content']}\n"
                            elif msg["role"] == "assistant":
                                if isinstance(msg["content"], str):
                                    history_text += f"Assistant: {msg['content']}\n"
                        
                        result = self.get_aos_questions(
                            tool_input.get("project_type", ""),
                            tool_input.get("customer_phase", "discovery"),
                            tool_input.get("gathered_info", "{}"),
                            history_text
                        )
                        tool_results.append({"tool": tool_name, "result": result})
                        
                        if result.get("success"):
                            questions = result.get("questions", [])
                            if questions:
                                # Only ask 1-2 questions max, be conversational
                                limited_questions = questions[:2]
                                if len(limited_questions) == 1:
                                    assistant_response += f"\n\n{limited_questions[0]}"
                                else:
                                    assistant_response += f"\n\n{limited_questions[0]} Also, {limited_questions[1].lower()}"
                    
                    elif tool_name == "save_customer_project":
                        result = self.save_customer_project(tool_input["phone_number"], tool_input["project_info"])
                        tool_results.append({"tool": tool_name, "result": result})
                        # Note: Don't add to assistant_response as this is a background action
                    
                    elif tool_name == "calculate_project_requirements":
                        # Validate AOS requirements before calculations
                        validation = self.validate_aos_requirements(messages, "calculate_project_requirements")
                        
                        if not validation["can_proceed"]:
                            # Block calculations and guide to proper sequence (Enhanced AOS-NEPQ)
                            missing = validation["missing_requirements"]
                            
                            if "product_search_first" in missing:
                                assistant_response += "\n\nLet me first search for the perfect tile options for your project, then I'll calculate the exact requirements and pricing."
                            elif "room_and_dimensions" in missing:
                                assistant_response += "\n\n**Question 1 of 7:** What type of room are you working on? And most importantly, what are the exact measurements (length and width) of the area you're planning to tile?"
                            elif "problem_awareness" in missing:
                                assistant_response += "\n\n**Question 2 of 7:** So to me, it sounds like your current flooring situation is going 100% perfect for you. Is there anything you would change about your current flooring if you could?"
                            elif "style_preferences" in missing:
                                assistant_response += "\n\n**Question 3 of 7:** Now that I understand what's not working, what would your ideal tile situation look like? Do you have any specific style or color preferences in mind?"
                            elif "installation_method" in missing:
                                assistant_response += "\n\n**Question 4 of 7:** Will you be installing this yourself or working with a contractor?"
                            elif "timeline" in missing:
                                assistant_response += "\n\n**Question 5 of 7:** When are you hoping to start this project?"
                            elif "consequence_questions" in missing:
                                assistant_response += "\n\n**Question 6 of 7:** What happens if you don't do anything about this flooring issue and it continues for another 6-12 months? Have you thought about what that might cost you?"
                            elif "budget" in missing:
                                assistant_response += "\n\n**Question 7 of 7:** What's your budget range for this project? And how important is it for you to solve this now rather than later?"
                            
                            tool_results.append({
                                "tool": "validation_check", 
                                "result": validation,
                                "blocked_action": "calculate_project_requirements"
                            })
                        else:
                            # Requirements met - proceed with calculations
                            result = self.calculate_project_requirements(
                                tool_input["dimensions"],
                                tool_input.get("tile_size", "12x12"),
                                tool_input.get("tile_price", 4.99),
                                tool_input.get("pattern", "straight")
                            )
                            tool_results.append({"tool": tool_name, "result": result})
                            
                            # Only show calculation results if successful
                            if result.get("success"):
                                calc_data = result
                                calc_response = f"""
**Professional Project Calculation:**

📐 **Project Dimensions:** {calc_data['dimensions']}
• Base area: {calc_data['base_square_footage']} sq ft
• Waste factor: {calc_data['waste_factor_percent']}% (for {calc_data['pattern_type']} pattern)
• Total tile needed: {calc_data['total_square_footage_needed']} sq ft

📦 **Tile Requirements:**
• Boxes needed: {calc_data['boxes_needed']} boxes
• Total coverage: {calc_data['total_coverage']} sq ft
• Tile cost: ${calc_data['tile_cost']:.2f}

🔧 **Essential Materials:**
• Premium Thinset: {calc_data['materials_breakdown']['premium_thinset']['quantity']} bags - ${calc_data['materials_breakdown']['premium_thinset']['quantity'] * calc_data['materials_breakdown']['premium_thinset']['unit_price']:.2f}
• Grout: {calc_data['materials_breakdown']['grout']['quantity']} bags - ${calc_data['materials_breakdown']['grout']['quantity'] * calc_data['materials_breakdown']['grout']['unit_price']:.2f}
• Grout Sealer: ${calc_data['materials_breakdown']['grout_sealer']['unit_price']:.2f}
• Tile Spacers: ${calc_data['materials_breakdown']['tile_spacers']['unit_price']:.2f}
• Leveling System: ${calc_data['materials_breakdown']['leveling_system']['unit_price']:.2f}

💰 **Total Investment:**
• Tiles: ${calc_data['tile_cost']:.2f}
• Materials: ${calc_data['materials_cost']:.2f}
• **Complete Project Total: ${calc_data['total_project_cost']:.2f}**
"""
                                assistant_response += calc_response
                    
                    elif tool_name == "attempt_close":
                        result = self.attempt_close(
                            tool_input["project_summary"],
                            tool_input.get("timeline", "soon"),
                            tool_input.get("urgency_reason", "availability")
                        )
                        tool_results.append({"tool": tool_name, "result": result})
                        
                        if result.get("success"):
                            close_response = f"""

{result['urgency_message']} {result['direct_close']}

**Next Steps:**
• {' • '.join(result['next_steps'])}

{result['urgency_close']}"""
                            assistant_response += close_response
            
            # Generate NEPQ conversation analysis and scoring
            nepq_analysis = self._generate_nepq_analysis(messages, phone_number)
            
            return {
                "success": True,
                "response": assistant_response,
                "tool_calls": tool_results,
                "conversation_updated": True,
                "nepq_analysis": nepq_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm experiencing some technical difficulties. Please try again."
            }

    def _generate_nepq_analysis(self, conversation_history: List[Dict], phone_number: str = None) -> Dict[str, Any]:
        """Generate NEPQ conversation analysis and scoring"""
        try:
            # Extract customer info
            customer_info = {
                'phone': phone_number or 'unknown',
                'name': self._extract_customer_name(conversation_history),
                'mode': 'customer'  # Default mode, can be enhanced later
            }
            
            # Generate comprehensive NEPQ analysis
            analysis = self.nepq_scorer.analyze_conversation(conversation_history, customer_info)
            
            # Generate performance report
            report = self.nepq_scorer.generate_report(analysis)
            
            # Save analysis to file for tracking (optional)
            try:
                file_path = f"reports/nepq_analysis_{analysis.conversation_id}.json"
                self.nepq_scorer.save_analysis(analysis, file_path)
            except Exception as e:
                logger.warning(f"Could not save NEPQ analysis: {e}")
            
            # Return analysis summary for immediate use
            return {
                "conversation_id": analysis.conversation_id,
                "overall_score": analysis.overall_score,
                "stage_scores": {
                    "connection": analysis.connection_score.score,
                    "problem_awareness": analysis.problem_awareness_score.score,
                    "consequence_discovery": analysis.consequence_discovery_score.score,
                    "solution_awareness": analysis.solution_awareness_score.score,
                    "qualifying_questions": analysis.qualifying_questions_score.score,
                    "objection_handling": analysis.objection_handling_score.score,
                    "commitment_stage": analysis.commitment_stage_score.score
                },
                "performance_grade": self._calculate_performance_grade(analysis.overall_score),
                "top_strengths": analysis.strengths[:3],  # Top 3 strengths
                "improvement_focus": analysis.next_conversation_focus[:2],  # Top 2 focus areas
                "detailed_report": report,
                "metrics": {
                    "questions_asked": analysis.questions_asked,
                    "objections_encountered": analysis.objections_encountered,
                    "objections_resolved": analysis.objections_resolved,
                    "conversation_length": analysis.conversation_length
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating NEPQ analysis: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "performance_grade": "Error",
                "stage_scores": {},
                "improvement_focus": ["Fix analysis system"]
            }
    
    def _extract_customer_name(self, conversation_history: List[Dict]) -> str:
        """Extract customer name from conversation"""
        import re
        
        for message in conversation_history:
            if message.get('role') == 'user':
                content = message.get('content', '').lower()
                
                # Look for name patterns
                name_patterns = [
                    r"my name is (\w+)",
                    r"i'm (\w+)",
                    r"call me (\w+)",
                    r"this is (\w+)"
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, content)
                    if match:
                        return match.group(1).title()
        
        return "Unknown"
    
    def _calculate_performance_grade(self, overall_score: float) -> str:
        """Calculate letter grade based on overall score"""
        if overall_score >= 90:
            return "A+ (Excellent)"
        elif overall_score >= 80:
            return "A (Very Good)"
        elif overall_score >= 70:
            return "B (Good)"
        elif overall_score >= 60:
            return "C (Acceptable)"
        elif overall_score >= 50:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"
    
    def generate_self_analysis_report(self, conversation_history: List[Dict], phone_number: str = None) -> str:
        """Generate comprehensive self-analysis report for agent improvement"""
        try:
            nepq_analysis = self._generate_nepq_analysis(conversation_history, phone_number)
            
            report = f"""
# 🤖 AI Agent Self-Analysis Report

**Conversation ID:** {nepq_analysis.get('conversation_id', 'N/A')}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Overall Performance:** {nepq_analysis.get('overall_score', 0):.1f}/100 ({nepq_analysis.get('performance_grade', 'N/A')})

## 📊 NEPQ Stage Performance (7-Point Scale)

| Stage | Score | Performance |
|-------|-------|-------------|
| Connection & Status | {nepq_analysis['stage_scores'].get('connection', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('connection', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('connection', 0) >= 6 else '🔴'} |
| Problem Awareness | {nepq_analysis['stage_scores'].get('problem_awareness', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('problem_awareness', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('problem_awareness', 0) >= 6 else '🔴'} |
| Consequence Discovery | {nepq_analysis['stage_scores'].get('consequence_discovery', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('consequence_discovery', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('consequence_discovery', 0) >= 6 else '🔴'} |
| Solution Awareness | {nepq_analysis['stage_scores'].get('solution_awareness', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('solution_awareness', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('solution_awareness', 0) >= 6 else '🔴'} |
| Qualifying Questions | {nepq_analysis['stage_scores'].get('qualifying_questions', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('qualifying_questions', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('qualifying_questions', 0) >= 6 else '🔴'} |
| Objection Handling | {nepq_analysis['stage_scores'].get('objection_handling', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('objection_handling', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('objection_handling', 0) >= 6 else '🔴'} |
| Commitment Stage | {nepq_analysis['stage_scores'].get('commitment_stage', 0)}/10 | {'🟢' if nepq_analysis['stage_scores'].get('commitment_stage', 0) >= 8 else '🟡' if nepq_analysis['stage_scores'].get('commitment_stage', 0) >= 6 else '🔴'} |

## 📈 Conversation Metrics

- **Questions Asked:** {nepq_analysis['metrics'].get('questions_asked', 0)}
- **Objections Encountered:** {nepq_analysis['metrics'].get('objections_encountered', 0)}
- **Objections Resolved:** {nepq_analysis['metrics'].get('objections_resolved', 0)}
- **Resolution Rate:** {(nepq_analysis['metrics'].get('objections_resolved', 0) / max(1, nepq_analysis['metrics'].get('objections_encountered', 1))) * 100:.1f}%
- **Total Exchanges:** {nepq_analysis['metrics'].get('conversation_length', 0)}

## 🎯 Performance Strengths

{chr(10).join(f"• {strength}" for strength in nepq_analysis.get('top_strengths', ['No strengths identified']))}

## 🔧 Priority Improvement Areas

{chr(10).join(f"• {focus}" for focus in nepq_analysis.get('improvement_focus', ['No focus areas identified']))}

## 🎓 Learning Recommendations

### Immediate Actions:
1. **Focus on lowest-scoring NEPQ stage** - Prioritize improvement in weakest area
2. **Practice emotional engagement** - Use more "feel" vs "think" language
3. **Improve question ratio** - Aim for 70% prospect talking, 30% agent

### Next Conversation Goals:
- Increase overall score by 10-15 points
- Focus specifically on: {', '.join(nepq_analysis.get('improvement_focus', ['general improvement']))}
- Maintain strengths in: {', '.join(nepq_analysis.get('top_strengths', ['identified strengths']))}

### Training Focus:
- Review NEPQ methodology for weak stages
- Practice objection handling using 3-step formula (Clarify → Discuss → Diffuse)
- Strengthen emotional positioning and internal tension creation

---

## 📋 Detailed Performance Report

{nepq_analysis.get('detailed_report', 'Detailed report not available')}

---

*Self-analysis generated by NEPQ Scoring System v1.0*
*Report ID: {nepq_analysis.get('conversation_id', 'N/A')}*
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating self-analysis report: {e}")
            return f"Error generating self-analysis report: {str(e)}"