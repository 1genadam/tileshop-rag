#!/usr/bin/env python3
"""
Simple Tile Shop AI Agent - Natural LLM-based approach
Core Components: System Prompt + Message History + User Input + Tools
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import anthropic

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
        
        # Core Component 1: System Prompt
        self.system_prompt = """You are Alex, a knowledgeable and friendly tile specialist at The Tile Shop. You're an expert in tiles, installation, and helping customers complete successful projects.

Your expertise includes:
- Helping customers find the perfect tiles for their projects
- Providing installation guidance for products they've purchased
- Recommending necessary installation accessories and tools
- Calculating quantities and project materials
- Troubleshooting installation issues

When customers ask about installation help:
1. IMPORTANT: If you see a phone number anywhere in the user's message (like "My phone number is: 847-302-2594"), immediately use the lookup_customer tool to verify their purchase history
2. If they mention a specific product but don't provide a phone number, ask for their phone number to look up their purchase history  
3. After using lookup_customer, provide specific installation guidance for their verified purchase
4. Recommend installation accessories: thinset, grout, sealer, sponges, trowels, wedges, leveling system, silicone, buckets, float

When customers ask about products:
- Use the search_products tool to find relevant tiles
- Ask about their project (room type, size, style preferences)
- Provide complete project recommendations including accessories

Be conversational and natural - like talking to a knowledgeable friend who works at a tile shop. Don't follow rigid scripts or phases. Just be helpful and use your tools when you need information."""

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