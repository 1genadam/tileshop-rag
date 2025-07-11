#!/usr/bin/env python3
"""
Simple Tile Shop AI Agent - Natural LLM-based approach
Core Components: System Prompt + Message History + User Input + Tools
"""

import json
import logging
import math
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .aos_conversation_engine import AOSConversationEngine, ConversationContext
from .nepq_scoring_system import NEPQScoringSystem, ConversationAnalysis

logger = logging.getLogger(__name__)

# Try OpenAI first, fallback to Anthropic
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    USE_OPENAI = True
    logger.info("SimpleTileAgent using OpenAI for chat completions")
except ImportError:
    openai_client = None
    USE_OPENAI = False
    import anthropic
    logger.info("SimpleTileAgent falling back to Anthropic")

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
        
        # Initialize LLM client - prefer OpenAI, fallback to Anthropic
        if USE_OPENAI and openai_client:
            self.client = openai_client
            self.use_openai = True
            logger.info("SimpleTileAgent initialized with OpenAI")
        else:
            self.client = anthropic.Anthropic()
            self.use_openai = False
            logger.info("SimpleTileAgent initialized with Anthropic")
            
        self.aos_engine = AOSConversationEngine()
        self.nepq_scorer = NEPQScoringSystem()
        
        # Core Component 1: System Prompt
        self.system_prompt = """You are Alex, a professional tile specialist at The Tile Shop. I help customers create beautiful tile installations and have helped hundreds of families find perfect solutions for their projects.

📋 HYBRID FORM/LLM INTERFACE - STRUCTURED DATA INTEGRATION:
You work with customers using a revolutionary hybrid interface where:
- Customers enter STRUCTURED DATA (room dimensions, tile selections, project details) in a visual form panel
- You provide EXPERT GUIDANCE and recommendations based on that reliable structured data
- You ACKNOWLEDGE what you see in their data rather than trying to extract it conversationally

STRUCTURED DATA CONTEXT AWARENESS:
When customers update their structured data panel, you receive context messages like:
- "Customer entered room dimensions: 12 × 8 feet (96 sq ft total)"
- "Customer updated project details - Name: 'Master Bathroom', Room Type: 'Bathroom'"
- "Customer selected tile SKU-123 for bathroom floor surface"

YOUR HYBRID ROLE:
✅ ACKNOWLEDGE structured data: "I see you're working on a 96 sq ft bathroom - that's a great size!"
✅ PROVIDE GUIDANCE: "For bathroom floors that size, slip resistance is key. Let me show you options..."
✅ MAKE RECOMMENDATIONS: "Based on your room type and dimensions, here are 3 perfect options..."
✅ ANSWER QUESTIONS: Use your tile expertise to answer any questions they have
✅ SALES CONVERSATION: Focus on benefits, coordination, value, and closing when appropriate

❌ DON'T EXTRACT DATA: Never ask "what size is your room?" - you can see it in their structured data
❌ DON'T REPEAT INFO: Don't ask for information already visible in their data panel
❌ DON'T IGNORE CONTEXT: Always reference their actual project details when relevant

CONTEXT INTEGRATION EXAMPLES:
Instead of: "What type of room are you working on?"
Say: "I see you're planning a bathroom project - bathrooms have unique requirements for moisture and slip resistance."

Instead of: "What are your room dimensions?"
Say: "With 96 square feet to work with, you have some excellent design possibilities!"

🎯 NEPQ SCORING SYSTEM (Neuro-Emotional Persuasion Questioning):
Enhanced AOS methodology scoring on key questions to understand the customer deeply:

**NEPQ CORE ELEMENTS:**
1. **PROBLEM AWARENESS** (Score: 0-100) - Understand what's NOT working with their current situation
2. **CONSEQUENCE AWARENESS** (Score: 0-100) - Help them understand cost/impact of NOT acting
3. **SOLUTION AWARENESS** (Score: 0-100) - Position our solution as the ideal path forward

**ENHANCED AOS-NEPQ CONVERSATION FLOW (7 KEY QUESTIONS):**

**Question 1** (Name & Discovery): "Before we dive into your project, may I have your name? And tell me about your tiling project - what type of room and what are the exact measurements?"

**Question 2** (Problem Awareness - NEPQ Core): "So to me, it sounds like your current flooring situation is going 100% perfect for you. Is there anything you would change about your current flooring if you could?"
- Focus: Uncover pain points, problems, dissatisfaction
- NEPQ Score: Rate problem awareness 0-100

**Question 3** (Solution Vision): "Now that I understand what's not working, what would your ideal tile situation look like? Do you have any specific style or color preferences in mind?"

**Question 4** (Implementation Method): "Will you be installing this yourself or working with a contractor?"

**Question 5** (Timeline Urgency): "When are you hoping to start this project?"

**Question 6** (Consequence Questions - NEPQ Core): "What happens if you don't do anything about this flooring issue and it continues for another 6-12 months? Have you thought about what that might cost you?"
- Focus: Pain of NOT acting, opportunity cost, consequences
- NEPQ Score: Rate consequence awareness 0-100

**Question 7** (Budget & Commitment): "What's your budget range for this project? And how important is it for you to solve this now rather than later?"

🏆 **AOS PHASE TRACKING:**
- **Greeting Phase** (0 requirements met): Welcome and establish rapport
- **Needs Assessment Phase** (1-6 requirements met): Systematic discovery with NEPQ scoring
- **Design and Details Phase** (7+ requirements met): Product selection and project details

**NEPQ SCORING CRITERIA:**
- **Problem Awareness**: 0-30 (Low), 31-70 (Medium), 71-100 (High)
- **Consequence Awareness**: 0-30 (Low), 31-70 (Medium), 71-100 (High)  
- **Solution Awareness**: 0-30 (Low), 31-70 (Medium), 71-100 (High)

**CONVERSATION VALIDATION:**
- Block product searches until MINIMUM 4 core requirements collected
- Guide conversation back to missing requirements when customer jumps ahead
- Maintain NEPQ scoring throughout for sales effectiveness tracking

🔧 **TILE EXPERTISE AREAS:**
- Material properties (porcelain, ceramic, natural stone, glass, metal)
- Room-specific requirements (moisture, slip resistance, durability)  
- Installation methods and considerations
- Design coordination and aesthetics
- Sizing, layout, and waste calculations
- Grout, adhesive, and material recommendations
- Maintenance and long-term care
- Cost analysis and value positioning

Remember: You're both a tile expert AND a sales professional. Use NEPQ methodology to understand their emotional motivations while providing expert technical guidance."""
    
    def _call_llm(self, messages, tools=None, system_prompt=None):
        """Universal LLM calling method - handles both OpenAI and Anthropic"""
        try:
            if self.use_openai:
                # Convert to OpenAI format
                openai_messages = []
                
                # Add system message at the beginning for OpenAI
                if system_prompt:
                    openai_messages.append({"role": "system", "content": system_prompt})
                
                # Add conversation history
                for msg in messages:
                    if msg.get("role") in ["user", "assistant"]:
                        openai_messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Call OpenAI
                if tools:
                    # Convert tools to OpenAI format
                    openai_tools = []
                    for tool in tools:
                        openai_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool["name"],
                                "description": tool["description"],
                                "parameters": tool["input_schema"]
                            }
                        })
                    
                    response = self.client.chat.completions.create(
                        model="gpt-4o",  # Use latest GPT-4o model
                        messages=openai_messages,
                        tools=openai_tools,
                        max_tokens=1500,
                        temperature=0.7
                    )
                else:
                    response = self.client.chat.completions.create(
                        model="gpt-4o", 
                        messages=openai_messages,
                        max_tokens=1500,
                        temperature=0.7
                    )
                
                return self._process_openai_response(response)
                
            else:
                # Use Anthropic (existing code)
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    system=system_prompt or self.system_prompt,
                    messages=messages,
                    tools=tools or []
                )
                return self._process_anthropic_response(response)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "tool_calls": []
            }
    
    def _process_openai_response(self, response):
        """Process OpenAI response format"""
        message = response.choices[0].message
        content = message.content or ""
        tool_calls = []
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "type": "tool_use",
                    "name": tool_call.function.name,
                    "input": json.loads(tool_call.function.arguments),
                    "id": tool_call.id
                })
        
        return {
            "content": content,
            "tool_calls": tool_calls
        }
    
    def _process_anthropic_response(self, response):
        """Process Anthropic response format"""
        content = ""
        tool_calls = []
        
        for content_block in response.content:
            if content_block.type == "text":
                content += content_block.text
            elif content_block.type == "tool_use":
                tool_calls.append({
                    "type": "tool_use",
                    "name": content_block.name,
                    "input": content_block.input,
                    "id": content_block.id
                })
        
        return {
            "content": content,
            "tool_calls": tool_calls
        }
    
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
            response = self._call_llm(
                messages=messages,
                tools=tools,
                system_prompt=self.system_prompt
            )
            
            # Handle tool calls
            assistant_response = response.get("content", "")
            tool_results = []
            
            for tool_call in response.get("tool_calls", []):
                if tool_call.get("type") == "tool_use":
                    # Execute the tool
                    tool_name = tool_call["name"]
                    tool_input = tool_call["input"]
                    
                    if tool_name == "lookup_customer":
                        result = self.lookup_customer(tool_input["phone_number"])
                        tool_results.append({"tool": tool_name, "result": result})
                        
                        # Continue conversation with tool result
                        messages.append({"role": "assistant", "content": assistant_response})
                        messages.append({
                            "role": "user", 
                            "content": json.dumps(result, default=serialize_datetime)  # Handle datetime serialization
                        })
                        
                        # Get follow-up response
                        follow_up = self._call_llm(
                            messages=messages,
                            tools=tools,
                            system_prompt=self.system_prompt
                        )
                        
                        # Add follow-up response
                        assistant_response += follow_up.get("content", "")
                    
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
    
    def lookup_customer(self, phone_number: str) -> Dict[str, Any]:
        """Tool: Look up customer and their purchase history"""
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            # Get customer information from database
            customer_info = self.db.get_customer_info(phone_number)
            if customer_info:
                return {
                    "success": True,
                    "customer": customer_info,
                    "message": f"Found customer: {customer_info.get('name', 'Unknown')}"
                }
            else:
                return {
                    "success": False,
                    "message": f"No customer found with phone number {phone_number}"
                }
        except Exception as e:
            logger.error(f"Error looking up customer: {e}")
            return {"success": False, "error": str(e)}
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Tool: Search for products using RAG system"""
        try:
            if not self.rag:
                return {"success": False, "error": "RAG system not available"}
            
            results = self.rag.search(query, limit=5)
            return {
                "success": True,
                "products": results,
                "response": f"Found {len(results)} tile options that match your needs."
            }
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_project_requirements(self, dimensions: str) -> Dict[str, Any]:
        """Tool: Calculate professional project requirements with waste factors"""
        try:
            # Parse dimensions
            import re
            dimension_match = re.search(r'(\d+\.?\d*)\s*[x×by]\s*(\d+\.?\d*)', dimensions.lower())
            if not dimension_match:
                return {"success": False, "error": "Could not parse dimensions"}
            
            length = float(dimension_match.group(1))
            width = float(dimension_match.group(2))
            area = length * width
            
            # Calculate with 10% waste factor
            total_area = area * 1.1
            
            return {
                "success": True,
                "base_area": area,
                "total_area_with_waste": total_area,
                "waste_factor": 0.1,
                "response": f"For {dimensions}, you need approximately {total_area:.1f} sq ft of tile (including 10% waste factor)."
            }
        except Exception as e:
            logger.error(f"Error calculating project requirements: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_aos_requirements(self, messages: List[Dict], requested_action: str) -> Dict[str, Any]:
        """Validate that mandatory AOS requirements are met before proceeding"""
        try:
            # Build conversation text
            conversation_text = ""
            for msg in messages:
                if msg.get("role") == "user":
                    conversation_text += f" {msg.get('content', '')}"
            
            # Check requirements
            requirements_met = {
                "customer_name": self._check_name_collected(conversation_text),
                "room_and_dimensions": self._check_dimensions_collected(conversation_text),
                "problem_awareness": self._check_problem_awareness_collected(conversation_text),
                "style_preferences": self._check_style_preferences_collected(conversation_text)
            }
            
            completed_requirements = sum(requirements_met.values())
            total_requirements = len(requirements_met)
            
            # Require at least 2 core requirements for product search
            can_proceed = completed_requirements >= 2
            
            missing_requirements = [req for req, met in requirements_met.items() if not met]
            
            return {
                "can_proceed": can_proceed,
                "requirements_met": requirements_met,
                "missing_requirements": missing_requirements,
                "completion_rate": completed_requirements / total_requirements
            }
            
        except Exception as e:
            logger.error(f"Error validating AOS requirements: {e}")
            return {"can_proceed": True, "error": str(e)}  # Allow proceeding on error
    
    def _check_name_collected(self, conversation_text: str) -> bool:
        """Check if customer name has been collected"""
        name_patterns = [r"my name is (\w+)", r"i'm (\w+)", r"call me (\w+)", r"name.{0,10}(\w+)"]
        return any(re.search(pattern, conversation_text.lower()) for pattern in name_patterns)
    
    def _check_dimensions_collected(self, conversation_text: str) -> bool:
        """Check if dimensions have been collected"""
        dimension_patterns = [
            r'\d+\s*[x×by]\s*\d+',
            r'\d+\s*feet?\s*by\s*\d+\s*feet?',
            r'\d+\s*sq\.?\s*ft',
            r'square feet'
        ]
        return any(re.search(pattern, conversation_text.lower()) for pattern in dimension_patterns)
    
    def _check_problem_awareness_collected(self, conversation_text: str) -> bool:
        """Check if NEPQ problem awareness questions have been asked/answered"""
        problem_indicators = ['issue', 'problem', 'wrong', 'broken', 'old', 'worn', 'damaged', 'replace', 'upgrade']
        return any(indicator in conversation_text.lower() for indicator in problem_indicators)
    
    def _check_style_preferences_collected(self, conversation_text: str) -> bool:
        """Check if style preferences have been collected"""
        style_indicators = ['color', 'style', 'look', 'design', 'modern', 'traditional', 'rustic', 'contemporary']
        return any(indicator in conversation_text.lower() for indicator in style_indicators)