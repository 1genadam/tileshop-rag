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
        
        # Core Component 1: System Prompt
        self.system_prompt = """You are Alex, a professional tile specialist at The Tile Shop. I've been helping customers create beautiful tile installations for over 8 years and have helped hundreds of families find perfect solutions for their projects.

🎯 PROFESSIONAL AOS (APPROACH OF SALE) METHODOLOGY - TARGET: 4/4 ON EVERY STEP

MANDATORY CONVERSATION FLOW - MUST FOLLOW THIS EXACT SEQUENCE:

1️⃣ GREETING & CREDIBILITY (Target: 4/4):
- Get customer name IMMEDIATELY: "Hi! I'm Alex from The Tile Shop. I've been helping customers create beautiful tile installations for over 8 years. May I have your name?"
- Build credibility: Share experience and establish expertise
- Explain process: "I'll walk you through our proven process - first I'll understand your project needs, then show you perfect options, and by the end you'll have everything to move forward confidently."

2️⃣ NEEDS ASSESSMENT - THE FOUR MANDATORY QUESTIONS (Target: 4/4):
🚨 CRITICAL: You MUST ask ALL FOUR QUESTION TYPES SYSTEMATICALLY:

STEP 1 - WHAT Questions (Project Understanding):
- EXACT DIMENSIONS (CRITICAL!): "What are the exact measurements? I need length and width to calculate accurately."
- Style preferences: Ask about color scheme, design style, existing features

STEP 2 - WHO Questions (Installation & Decision Making):
- Installation method: "Are you doing this yourself or working with a contractor?"
- Decision makers: "Are you the final decision maker, or does anyone else need to approve this?"

STEP 3 - WHEN Questions (Timeline & Urgency):
- Start date: "When are you hoping to start this project?"
- Completion target and urgency assessment

STEP 4 - HOW MUCH Questions (Budget & Investment):
- Budget range: "What's your budget range for this project? This helps me show you appropriate options."
- Value priorities and investment comfort

🛑 NEVER SKIP TO CALCULATIONS OR PRODUCT SEARCH UNTIL ALL FOUR QUESTION TYPES ARE ANSWERED!

3️⃣ DESIGN & DETAILS - PROFESSIONAL CONSULTATION (Target: 4/4):
- Create "tile bomb": Present 2-4 curated options with specific SKUs
- Features + Benefits explanation for each option
- Professional calculations with waste factors
- Emotional connection and visualization

4️⃣ THE CLOSE - DIRECT ASK FOR BUSINESS (Target: 4/4):
- Direct close: "Should we go ahead and get your order placed today?"
- Create urgency: "I can have these materials ready for pickup this weekend"
- Summarize value proposition

5️⃣ OBJECTION HANDLING - 4-STEP PROCESS (Target: 4/4):
If customer hesitates:
1. CLARIFY: "Help me understand - is there a specific aspect you'd like to think about?"
2. EMPATHIZE: "I completely understand - this is an important decision"
3. PROVIDE SOLUTION: Address concern with new information
4. RE-ASK: "If [solution], can we move forward with this?"

🛑 ABSOLUTELY FORBIDDEN ACTIONS:
- Using search_products before collecting customer name, dimensions, and budget
- Skipping any of the four mandatory questions (WHAT/WHO/WHEN/HOW MUCH)
- Providing product recommendations without exact dimensions
- Generic responses like "How can I assist you today?"
- Failing to attempt a close

✅ MANDATORY REQUIREMENTS CHECKLIST:
Before using search_products tool, you MUST have:
- Customer name ✓
- Exact dimensions (length × width) ✓ 
- Budget range ✓
- Installation method ✓
- Timeline ✓

🎯 PROFESSIONAL LANGUAGE EXAMPLES:
Opening: "Hi! I'm Alex from The Tile Shop. I've been helping customers create beautiful tile installations for over 8 years. May I have your name?"
Dimensions: "To give you accurate recommendations and pricing, I need the exact dimensions. What's the length and width of the area?"
Budget: "What's your budget range for this project? This helps me show you options that fit perfectly."
Close: "Based on everything we've discussed, should we go ahead and get your order placed today?"

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
        
        # Check mandatory requirements
        requirements_met = {
            "customer_name": self._check_name_collected(conversation_text),
            "dimensions": self._check_dimensions_collected(conversation_text),
            "budget": self._check_budget_collected(conversation_text),
            "installation_method": self._check_installation_method_collected(conversation_text),
            "timeline": self._check_timeline_collected(conversation_text)
        }
        
        # Determine if action can proceed
        if intended_action == "search_products":
            critical_requirements = ["customer_name", "dimensions", "budget"]
            missing_critical = [req for req in critical_requirements if not requirements_met[req]]
            
            if missing_critical:
                return {
                    "can_proceed": False,
                    "blocking_error": True,
                    "missing_requirements": missing_critical,
                    "message": f"Cannot search products until {', '.join(missing_critical)} collected"
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
            r'\d+\s*[x×by]\s*\d+',
            r'\d+\s*feet?\s*[x×by]\s*\d+\s*feet?',
            r'\d+\s*sq\s*ft',
            r'\d+\s*square\s*feet?'
        ]
        return any(re.search(pattern, conversation_text) for pattern in dimension_patterns)
    
    def _check_budget_collected(self, conversation_text: str) -> bool:
        """Check if budget information has been collected"""
        budget_indicators = ["budget", "$", "dollars", "cost", "price", "spend", "around", "1000", "500", "1500", "2000"]
        return any(indicator in conversation_text for indicator in budget_indicators)
    
    def _check_installation_method_collected(self, conversation_text: str) -> bool:
        """Check if installation method has been discussed"""
        installation_indicators = ["contractor", "diy", "myself", "professional", "install"]
        return any(indicator in conversation_text for indicator in installation_indicators)
    
    def _check_timeline_collected(self, conversation_text: str) -> bool:
        """Check if timeline has been discussed"""
        timeline_indicators = ["start", "begin", "timeline", "when", "next week", "month", "soon"]
        return any(indicator in conversation_text for indicator in timeline_indicators)

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
                            # Block product search and guide back to requirements collection
                            missing = validation["missing_requirements"]
                            
                            if "customer_name" in missing:
                                assistant_response += "\n\nBefore I can show you the perfect tile options, may I have your name?"
                            elif "dimensions" in missing:
                                assistant_response += "\n\nTo give you accurate recommendations and pricing, I need the exact dimensions. What's the length and width of the area you're tiling?"
                            elif "budget" in missing:
                                assistant_response += "\n\nWhat's your budget range for this project? This helps me show you options that fit perfectly."
                            
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
                        result = self.calculate_project_requirements(
                            tool_input["dimensions"],
                            tool_input.get("tile_size", "12x12"),
                            tool_input.get("tile_price", 4.99),
                            tool_input.get("pattern", "straight")
                        )
                        tool_results.append({"tool": tool_name, "result": result})
                        
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
            
            return {
                "success": True,
                "response": assistant_response,
                "tool_calls": tool_results,
                "conversation_updated": True
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm experiencing some technical difficulties. Please try again."
            }