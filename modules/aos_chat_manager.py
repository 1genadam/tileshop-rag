#!/usr/bin/env python3
"""
AOS Chat Manager - Implements The Tile Shop's Approach of Sale methodology
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class AOSScorer:
    """Automatic AOS phase scoring system"""
    
    def __init__(self):
        self.scoring_weights = {
            'greeting': {
                'got_name': 1.0,
                'used_name': 0.5,
                'asked_about_project': 0.8,
                'built_credibility': 0.7
            },
            'needs_assessment': {
                'got_what': 1.0,    # Project details
                'got_who': 0.8,     # Installation method
                'got_when': 0.6,    # Timeline
                'got_how_much': 0.6 # Budget
            },
            'design_details': {
                'showed_products': 1.0,
                'explained_benefits': 0.8,
                'addressed_concerns': 0.7,
                'narrowed_choices': 0.6
            },
            'close': {
                'asked_for_business': 1.0,
                'recognized_buying_signals': 0.8,
                'overcame_objections': 0.7
            }
        }
    
    def score_greeting_phase(self, conversation_data: Dict) -> int:
        """Score greeting phase automatically"""
        score = 0
        
        # Check if we got customer name
        if conversation_data.get('customer_name'):
            score += 1.0
        
        # Check if we used their name in responses
        if conversation_data.get('name_usage_count', 0) > 0:
            score += 0.5
        
        # Check if we asked about their project
        if conversation_data.get('project_inquiry_made'):
            score += 0.8
        
        # Check if we built credibility
        if conversation_data.get('credibility_statements', 0) > 0:
            score += 0.7
        
        return min(4, max(1, round(score)))
    
    def score_needs_assessment_phase(self, collected_info: Dict) -> int:
        """Score needs assessment completeness"""
        score = 0
        
        # WHAT - Project details
        if collected_info.get('project_type') and collected_info.get('surface_area_sf'):
            score += 1.0
        
        # WHO - Installation method
        if collected_info.get('installation_method'):
            score += 0.8
        
        # WHEN - Timeline
        if collected_info.get('project_timeline'):
            score += 0.6
        
        # HOW MUCH - Budget
        if collected_info.get('budget_range'):
            score += 0.6
        
        return min(4, max(1, round(score)))
    
    def score_design_phase(self, conversation_data: Dict) -> int:
        """Score design consultation effectiveness"""
        score = 0
        
        # Showed product options
        if conversation_data.get('products_shown', 0) >= 2:
            score += 1.0
        
        # Explained benefits
        if conversation_data.get('benefits_explained', 0) > 0:
            score += 0.8
        
        # Addressed concerns
        if conversation_data.get('concerns_addressed', 0) > 0:
            score += 0.7
        
        # Narrowed down choices
        if conversation_data.get('selection_made'):
            score += 0.6
        
        return min(4, max(1, round(score)))
    
    def score_close_phase(self, conversation_data: Dict) -> int:
        """Score closing effectiveness"""
        score = 0
        
        # Asked for business directly
        if conversation_data.get('direct_close_attempted'):
            score += 1.0
        
        # Recognized buying signals
        if conversation_data.get('buying_signals_detected', 0) > 0:
            score += 0.8
        
        # Overcame objections
        if conversation_data.get('objections_handled', 0) > 0:
            score += 0.7
        
        return min(4, max(1, round(score)))

class AOSChatManager:
    """Manages AOS-based conversations with customers"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.scorer = AOSScorer()
        
        # Conversation state tracking
        self.current_sessions = {}  # In-memory session state
        
        # Initialize LLM for conversational responses
        self.llm_client = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client for conversational responses"""
        try:
            import anthropic
            import os
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.llm_client = anthropic.Anthropic(api_key=api_key)
                logger.info("LLM client initialized for conversational AOS responses")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
            self.llm_client = None
    
    def generate_conversational_response(self, aos_response: str, query: str, aos_phase: str, customer_info: Dict = None) -> str:
        """Generate a more conversational version of the AOS response using LLM"""
        if not self.llm_client:
            return aos_response
            
        try:
            customer_name = customer_info.get('first_name', '') if customer_info else ''
            
            prompt = f"""You are a friendly, conversational tile expert at The Tile Shop. Transform the following structured AOS response into a more natural, conversational response that maintains the same information and sales process but sounds more human and engaging.

Customer Query: "{query}"
AOS Phase: {aos_phase}
Customer Name: {customer_name or 'Unknown'}

Original AOS Response:
{aos_response}

Transform this into a conversational response that:
1. Sounds natural and friendly
2. Maintains all the essential information and questions
3. Uses a warm, helpful tone
4. Guides the customer naturally through the sales process
5. Includes the customer's name if available
6. Feels like talking to a knowledgeable friend, not a script

Keep the response concise but warm. If there are specific questions or next steps, make them feel like natural conversation rather than a checklist."""

            response = self.llm_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            conversational_response = response.content[0].text
            logger.info(f"Generated conversational response for {aos_phase} phase")
            return conversational_response
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            return aos_response
    
    def detect_aos_phase(self, query: str, conversation_context: Dict = None) -> str:
        """Detect which AOS phase we're in based on query and conversation history"""
        query_lower = query.lower().strip()
        
        # If we have conversation context, use it to make smarter decisions
        if conversation_context:
            current_phase = conversation_context.get('current_phase', 'greeting')
            collected_info = conversation_context.get('collected_info', {})
            conversation_history = conversation_context.get('conversation_history', [])
            
            # Check if customer has provided their name and we're past greeting
            if (current_phase == 'greeting' and 
                conversation_context.get('customer', {}).get('first_name') and
                len(conversation_history) > 0):
                # If customer is providing project details, move to needs assessment
                if any(pattern in query_lower for pattern in ['looking for', 'need', 'want', 'floor', 'bathroom', 'kitchen', 'tile', 'diy', 'contractor']):
                    return 'needs_assessment'
                # If customer is providing name/phone info, stay in greeting
                elif any(pattern in query_lower for pattern in ['847', '302', '2594', 'robert']) and len(query_lower.split()) <= 3:
                    return 'greeting'
            
            # If we're in needs assessment and have some info, check for progression
            if current_phase == 'needs_assessment':
                # Count how much info we have collected
                info_fields = ['project_type', 'installation_method', 'project_timeline', 'budget_range', 'surface_area_sf']
                collected_count = sum(1 for field in info_fields if collected_info.get(field))
                
                # If we have most info and customer is asking about products, move to design
                if collected_count >= 2 and any(pattern in query_lower for pattern in ['show me', 'options', 'styles', 'colors', 'which tile', 'recommend']):
                    return 'design_details'
                # If customer is asking about pricing, move to close
                elif any(pattern in query_lower for pattern in ['price', 'cost', 'how much', 'quote']):
                    return 'close'
                # Otherwise stay in needs assessment
                else:
                    return 'needs_assessment'
            
            # If we're in design phase and customer is asking about pricing/ordering
            if current_phase == 'design_details':
                if any(pattern in query_lower for pattern in ['price', 'cost', 'order', 'buy', 'purchase', 'how much', 'quote']):
                    return 'close'
                else:
                    return 'design_details'
            
            # If we're in close phase, stay there unless customer has new questions
            if current_phase == 'close':
                if any(pattern in query_lower for pattern in ['show me', 'options', 'different', 'other']):
                    return 'design_details'
                else:
                    return 'close'
        
        # Fallback to pattern matching for new conversations
        # Greeting indicators
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'welcome']
        if any(pattern in query_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Needs assessment indicators
        needs_patterns = ['looking for', 'need', 'want', 'project', 'renovating', 'redoing', 'installing', 'floor', 'bathroom', 'kitchen']
        if any(pattern in query_lower for pattern in needs_patterns):
            return 'needs_assessment'
        
        # Design phase indicators
        design_patterns = ['show me', 'options', 'styles', 'colors', 'which tile', 'recommend']
        if any(pattern in query_lower for pattern in design_patterns):
            return 'design_details'
        
        # Close indicators
        close_patterns = ['price', 'cost', 'order', 'buy', 'purchase', 'how much', 'quote']
        if any(pattern in query_lower for pattern in close_patterns):
            return 'close'
        
        # Default to greeting for new conversations
        return 'greeting'
    
    def handle_greeting_phase(self, query: str, customer: Dict = None, conversation_context: Dict = None) -> str:
        """Handle AOS greeting phase"""
        # Check if this is a returning customer or if we already have their info
        if customer and customer.get('first_name'):
            customer_name = customer['first_name']
            # Check if this is truly a greeting or if customer is providing project info
            if any(pattern in query.lower() for pattern in ['looking for', 'need', 'want', 'floor', 'bathroom', 'kitchen', 'tile']):
                return f"Perfect, {customer_name}! I can see you're interested in tiles for your project. Let me help you find exactly what you need. What type of space are you working on?"
            else:
                return f"Welcome back, {customer_name}! I'm excited to help you with your tile project today. What brings you back to The Tile Shop?"
        else:
            return """Hello! Welcome to The Tile Shop. I'm here to help you find the perfect tile solution for your project. 

I've been helping customers create beautiful tile installations for several years, and I love seeing how the right tile choice can completely transform a space. 

May I have your name and phone number so I can provide you with personalized assistance?"""
    
    def handle_needs_assessment(self, query: str, customer: Dict, collected_info: Dict = None) -> str:
        """Handle AOS needs assessment phase"""
        if not collected_info:
            collected_info = {}
        
        # Check what information we still need
        missing_info = []
        
        if not collected_info.get('project_type'):
            missing_info.append('WHAT')
        if not collected_info.get('installation_method'):
            missing_info.append('WHO')
        if not collected_info.get('project_timeline'):
            missing_info.append('WHEN')
        if not collected_info.get('budget_range'):
            missing_info.append('HOW MUCH')
        
        if missing_info:
            first_missing = missing_info[0]
            
            if first_missing == 'WHAT':
                customer_name = customer['first_name'] if customer else "there"
                return f"""Perfect, {customer_name}! To make sure I recommend the absolute best options for you, let me understand your project better through our proven consultation process.

**WHAT**: Tell me about the specific area you're tiling - is this a kitchen backsplash, bathroom floor, shower walls, or something else? And can you give me the dimensions? For example, length and width for floors, or length and height for backsplashes?"""
            
            elif first_missing == 'WHO':
                customer_name = customer['first_name'] if customer else "Great"
                return f"""Excellent, {customer_name}! 

**WHO**: Are you planning to install this yourself, or will you be working with a contractor? If DIY, have you done tile work before?"""
            
            elif first_missing == 'WHEN':
                customer_name = customer['first_name'] if customer else "Excellent"
                return f"""Excellent, {customer_name}!

**WHEN**: Do you have a target date for when you'd like this completed? When are you hoping to start?"""
            
            elif first_missing == 'HOW MUCH':
                customer_name = customer['first_name'] if customer else "Perfect"
                return f"""Perfect, {customer_name}!

**HOW MUCH**: Do you have a budget range in mind for the tile portion of this project? This helps me show you options that fit your investment level."""
        
        else:
            # All needs assessment info collected, move to design phase
            customer_name = customer['first_name'] if customer else "Excellent"
            return f"""Excellent, {customer_name}! I have all the details I need about your {collected_info.get('project_type')} project. 

Based on your {collected_info.get('installation_method')} installation, {collected_info.get('project_timeline')} timeline, and {collected_info.get('budget_range')} budget, I have some fantastic tile options that would be perfect for your space.

Let me show you a few tiles that I think you'll love..."""
    
    def handle_design_phase(self, query: str, customer: Dict, products: List[Dict] = None) -> str:
        """Handle AOS design and details phase"""
        if not products:
            # Need to get product recommendations
            customer_name = customer['first_name'] if customer else ""
            return f"""Based on what you've told me about your project{', ' + customer_name if customer_name else ''}, I have some excellent options in mind. Let me search for the perfect tiles for your space...

Would you like to see tiles in a specific style - modern, traditional, rustic, or contemporary?"""
        
        # Present products with benefits
        customer_name = customer['first_name'] if customer else "Perfect"
        response = f"""Perfect, {customer_name}! Here are tiles that would work beautifully for your project:\n\n"""
        
        for i, product in enumerate(products[:3], 1):
            response += f"""**{i}. {product.get('title', 'Premium Tile')}** (SKU: {product.get('sku', 'N/A')})
💰 ${product.get('price_per_box', 'Contact for pricing')} per box
📐 {product.get('coverage', 'Standard coverage')}
🎨 {product.get('color', 'Beautiful finish')} - {product.get('finish', 'Premium quality')}

✨ **Why this works for you**: {self._generate_benefit_statement(product)}

"""
        
        customer_name = customer['first_name'] if customer else ""
        response += f"""Which of these resonates most with your vision{', ' + customer_name if customer_name else ''}? I can provide more details about any of these options or show you similar alternatives."""
        
        return response
    
    def handle_close_phase(self, query: str, customer: Dict, selected_product: Dict = None) -> str:
        """Handle AOS closing phase"""
        if selected_product:
            customer_name = customer['first_name'] if customer else "Excellent choice"
            return f"""Excellent choice, {customer_name}! The {selected_product.get('title')} is going to look absolutely stunning in your space. I can already picture how beautiful it's going to make your {selected_product.get('room_type', 'area')} feel.

Should we move forward with calculating the exact quantities you'll need and get your order placed today? I can also make sure we include all the necessary trim pieces and accessories to complete your project perfectly."""
        
        else:
            customer_name = customer['first_name'] if customer else ""
            return f"""I can see you're excited about these options{', ' + customer_name if customer_name else ''}! To help you make the best decision, which tile caught your eye the most? Once you let me know your preference, I can calculate exactly what you'll need and provide you with complete project pricing."""
    
    def _generate_benefit_statement(self, product: Dict) -> str:
        """Generate benefit statement based on product features"""
        benefits = []
        
        if 'porcelain' in product.get('title', '').lower():
            benefits.append("incredibly durable and water-resistant")
        
        if any(size in product.get('size_shape', '') for size in ['24x24', '24x48', '12x24']):
            benefits.append("large format creates a clean, modern look with fewer grout lines")
        
        if 'wood' in product.get('title', '').lower():
            benefits.append("gives you the warmth of wood without maintenance concerns")
        
        if 'marble' in product.get('title', '').lower():
            benefits.append("provides luxurious marble appearance at a fraction of the cost")
        
        return benefits[0] if benefits else "perfect quality and style for your project"
    
    def extract_information_from_query(self, query: str) -> Dict:
        """Extract customer information from their query using NLP patterns"""
        extracted = {}
        query_lower = query.lower()
        
        # Extract project type
        project_patterns = {
            'kitchen': ['kitchen', 'backsplash'],
            'bathroom': ['bathroom', 'bath'],
            'shower': ['shower'],
            'floor': ['floor', 'flooring'],
            'basement': ['basement'],
            'entryway': ['entryway', 'entry', 'foyer']
        }
        
        for project_type, patterns in project_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                extracted['project_type'] = project_type
                break
        
        # Extract dimensions
        dimension_match = re.search(r'(\d+)\s*[x×]\s*(\d+)', query)
        if dimension_match:
            extracted['length_ft'] = float(dimension_match.group(1))
            extracted['width_ft'] = float(dimension_match.group(2))
            extracted['surface_area_sf'] = extracted['length_ft'] * extracted['width_ft']
        
        # Extract installation method
        if any(word in query_lower for word in ['diy', 'myself', 'install myself']):
            extracted['installation_method'] = 'diy'
        elif any(word in query_lower for word in ['contractor', 'professional']):
            extracted['installation_method'] = 'contractor'
        
        # Extract timeline
        if any(word in query_lower for word in ['this week', 'immediately', 'asap']):
            extracted['project_timeline'] = 'within_1_week'
        elif any(word in query_lower for word in ['next week', 'soon']):
            extracted['project_timeline'] = 'within_2_weeks'
        elif any(word in query_lower for word in ['this month']):
            extracted['project_timeline'] = 'within_1_month'
        
        # Extract budget indicators
        budget_match = re.search(r'\$(\d+(?:,\d{3})*)', query)
        if budget_match:
            extracted['budget_range'] = budget_match.group(0)
        
        # **NEW: Extract purchase indicators and product mentions**
        # Detect if customer mentions they bought something
        purchase_indicators = ['bought', 'purchased', 'got from you', 'ordered', 'i have', 'already have']
        explicit_purchase_mention = any(indicator in query_lower for indicator in purchase_indicators)
        
        # Detect if customer is asking for installation help
        installation_help_indicators = ['how to install', 'installation', 'how do i', 'instructions', 'help with']
        needs_installation_help = any(indicator in query_lower for indicator in installation_help_indicators)
        
        # Extract specific product mentions
        # Prioritize specific products over generic ones
        specific_products = ['permat', 'backer-lite', 'heat mat', 'thinset', 'grout', 'adhesive', 'mortar']
        generic_products = ['tile']
        
        mentioned_product = None
        
        # Check specific products first
        for keyword in specific_products:
            if keyword in query_lower:
                mentioned_product = keyword
                break
        
        # If no specific product found, check generic products only if installation help is requested
        if not mentioned_product and needs_installation_help:
            for keyword in generic_products:
                if keyword in query_lower:
                    mentioned_product = keyword
                    break
        
        # Set purchase verification flags
        if explicit_purchase_mention:
            extracted['mentions_purchase'] = True
            if mentioned_product:
                extracted['mentioned_product'] = mentioned_product
        elif needs_installation_help and mentioned_product and mentioned_product in specific_products:
            # If asking for installation help with a specific product (not generic), assume they own it
            extracted['mentions_purchase'] = True
            extracted['mentioned_product'] = mentioned_product
            extracted['installation_inquiry'] = True  # Flag to indicate this came from installation request
        
        # Set installation help flag
        if needs_installation_help:
            extracted['needs_installation_help'] = True
        
        return extracted
    
    def should_vectorize_conversation(self, conversation_data: Dict, collected_info: Dict) -> bool:
        """Determine if conversation should be vectorized based on selective criteria"""
        # Calculate information completeness
        required_fields = ['customer_name', 'project_type', 'surface_area_sf', 'installation_method', 
                          'budget_range', 'project_timeline', 'style_preference']
        
        completed = sum(1 for field in required_fields if collected_info.get(field))
        info_completeness = completed / len(required_fields)
        
        # Check buying intent (within 2 weeks)
        timeline = collected_info.get('project_timeline', '')
        buying_intent_weeks = 999
        
        if 'within_1_week' in timeline:
            buying_intent_weeks = 0.5
        elif 'within_2_weeks' in timeline:
            buying_intent_weeks = 2
        elif 'within_1_month' in timeline:
            buying_intent_weeks = 4
        
        # Vectorize if 80%+ info gathered and buying within 2 weeks
        return (
            info_completeness >= 0.80 and 
            buying_intent_weeks <= 2 and
            conversation_data.get('aos_score_overall', 0) >= 3
        )
    
    def get_or_create_customer_session(self, phone_number: str, first_name: str = None) -> Dict:
        """Get or create customer and return session data with persistent conversation state"""
        try:
            # Get or create customer
            customer = self.db.get_or_create_customer(phone_number, first_name)
            
            if not customer:
                return None
            
            # Get or create active project
            project_id = self.db.create_customer_project(
                customer['customer_id'], 
                {'project_name': 'AI Chat Session'}
            )
            
            # Get or create conversation session with persistent state
            conversation_session = self.db.get_or_create_conversation_session(project_id)
            
            if not conversation_session:
                logger.error("Failed to create conversation session")
                return None
            
            # Initialize conversation_data if not present or if new session
            if conversation_session.get('is_new_session', False) or not conversation_session.get('conversation_data'):
                conversation_session['conversation_data'] = {
                    'customer_name': customer['first_name'] if customer else None,
                    'name_usage_count': 0,
                    'project_inquiry_made': False,
                    'credibility_statements': 0,
                    'products_shown': 0,
                    'benefits_explained': 0,
                    'concerns_addressed': 0,
                    'selection_made': False
                }
            
            # Merge customer and session data
            session_data = {
                'customer': customer,
                'project_id': project_id,
                'session_id': conversation_session['session_id'],
                'current_phase': conversation_session['current_phase'],
                'collected_info': conversation_session['collected_info'],
                'conversation_data': conversation_session['conversation_data'],
                'conversation_history': conversation_session['conversation_history'],
                'is_new_session': conversation_session.get('is_new_session', False)
            }
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating customer session: {e}")
            return None
    
    def process_chat_message(self, query: str, phone_number: str, first_name: str = None) -> Dict[str, Any]:
        """Process a chat message with full conversation context and state persistence"""
        try:
            # Get or create customer session with persistent state
            session = self.get_or_create_customer_session(phone_number, first_name)
            if not session:
                return {
                    'success': False,
                    'error': 'Failed to create customer session',
                    'response': 'I apologize, but I\'m having trouble accessing our system. Please try again.'
                }
            
            # Extract information from current query
            extracted_info = self.extract_information_from_query(query)
            
            # Update collected info with newly extracted information
            collected_info = session.get('collected_info', {})
            collected_info.update(extracted_info)
            
            # Add current exchange to conversation history
            conversation_history = session.get('conversation_history', [])
            conversation_history.append({
                'user_input': query,
                'timestamp': datetime.now().isoformat(),
                'extracted_info': extracted_info
            })
            
            # Detect the appropriate phase using full conversation context
            phase_before = session.get('current_phase', 'greeting')
            current_phase = self.detect_aos_phase(query, session)
            
            # Generate response based on phase
            if current_phase == 'greeting':
                response = self.handle_greeting_phase(query, session.get('customer'), session)
            elif current_phase == 'needs_assessment':
                response = self.handle_needs_assessment(query, session.get('customer'), collected_info)
            elif current_phase == 'design_details':
                response = self.handle_design_phase(query, session.get('customer'), None)
            elif current_phase == 'close':
                response = self.handle_close_phase(query, session.get('customer'), None)
            else:
                response = self.handle_greeting_phase(query, session.get('customer'), session)
            
            # Update conversation data
            conversation_data = session.get('conversation_data', {})
            conversation_data['name_usage_count'] = conversation_data.get('name_usage_count', 0) + (1 if session.get('customer', {}).get('first_name') in response else 0)
            conversation_data['project_inquiry_made'] = True if any(word in query.lower() for word in ['project', 'tile', 'floor', 'kitchen', 'bathroom']) else conversation_data.get('project_inquiry_made', False)
            
            # Add AI response to conversation history
            conversation_history.append({
                'ai_response': response,
                'timestamp': datetime.now().isoformat(),
                'phase': current_phase
            })
            
            # Update session state in database
            self.db.update_conversation_session(
                session['session_id'],
                current_phase,
                collected_info,
                conversation_data,
                conversation_history
            )
            
            # Add conversation turn to database
            self.db.add_conversation_turn(
                session['session_id'],
                len(conversation_history) // 2,  # Each turn has user input + AI response
                query,
                response,
                extracted_info,
                phase_before,
                current_phase
            )
            
            return {
                'success': True,
                'response': response,
                'session_id': session['session_id'],
                'current_phase': current_phase,
                'collected_info': collected_info,
                'conversation_data': conversation_data,
                'phase_changed': phase_before != current_phase
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'I apologize, but I\'m experiencing some technical difficulties. Please try again.'
            }
    
    def handle_purchase_verification(self, query: str, extracted_info: Dict, customer: Dict = None) -> Dict[str, Any]:
        """Handle purchase verification and product matching"""
        result = {
            'needs_phone_number': False,
            'verification_result': None,
            'response': '',
            'purchase_verified': False,
            'suggested_products': []
        }
        
        # If customer mentions purchase but no customer info, request phone number
        if extracted_info.get('mentions_purchase') and not customer:
            result['needs_phone_number'] = True
            
            # Customize message based on whether this is an installation inquiry
            if extracted_info.get('installation_inquiry'):
                result['response'] = f"""I'd be happy to help you with installing {extracted_info.get('mentioned_product', 'your product')}! To provide you with the most accurate installation instructions, could you please provide your phone number so I can look up your purchase history and make sure I'm giving you the right guidance for the specific product you bought?"""
            else:
                result['response'] = """I'd be happy to help you with your installation! To provide you with the most accurate guidance, could you please provide your phone number so I can look up your purchase history and make sure I'm giving you the right instructions for the specific product you bought?"""
            return result
        
        # If we have customer info and they mentioned a purchase, verify it
        if customer and extracted_info.get('mentions_purchase'):
            mentioned_product = extracted_info.get('mentioned_product', '')
            
            # Get customer purchase history
            purchases = self.db.get_customer_purchases(customer['customer_id'])
            
            # Find product match
            product_match = self.db.find_product_by_keyword(mentioned_product, purchases)
            
            result['verification_result'] = product_match
            
            if product_match['exact_match']:
                # Customer bought exactly what they mentioned
                purchased_product = product_match['exact_match']
                result['purchase_verified'] = True
                
                # Add installation guidance if this is an installation inquiry
                if extracted_info.get('installation_inquiry'):
                    installation_guidance = self._get_installation_guidance(product_match)
                    result['response'] = f"""Perfect! I can see you purchased {purchased_product['product_name']} on {purchased_product['order_date']}. Here are the specific installation instructions for your product:

{installation_guidance}"""
                else:
                    result['response'] = f"""Perfect! I can see you purchased {purchased_product['product_name']} on {purchased_product['order_date']}. I'll provide you with the specific installation instructions for this product."""
                
            elif product_match['customer_has_related']:
                # Customer bought related products
                related_purchase = product_match['customer_has_related'][0]
                purchased_product = related_purchase['purchased_product']
                category = related_purchase['category']
                
                result['purchase_verified'] = True
                
                # Add installation guidance if this is an installation inquiry
                if extracted_info.get('installation_inquiry'):
                    installation_guidance = self._get_installation_guidance(product_match)
                    result['response'] = f"""I see you mentioned "{mentioned_product}", but I found that you actually purchased {purchased_product['product_name']} on {purchased_product['order_date']}, which is a {category} product - very similar to what you mentioned! Here are the correct installation instructions for the {purchased_product['product_name']} that you actually bought:

{installation_guidance}"""
                else:
                    result['response'] = f"""I see you mentioned "{mentioned_product}", but I found that you actually purchased {purchased_product['product_name']} on {purchased_product['order_date']}, which is a {category} product - very similar to what you mentioned! Let me provide you with the correct installation instructions for the {purchased_product['product_name']} that you actually bought."""
                
            else:
                # No matching purchase found
                result['purchase_verified'] = False
                if purchases:
                    # Show what they did buy
                    recent_products = [p['product_name'] for p in purchases[:3]]
                    result['response'] = f"""I don't see "{mentioned_product}" in your recent purchase history. However, I do see you've purchased: {', '.join(recent_products)}. Could you clarify which product you need installation help with, or would you like assistance with one of these items instead?"""
                else:
                    result['response'] = f"""I don't see any recent purchases in our system for your phone number. Could you double-check the phone number, or if you purchased under a different number, please provide that instead? I want to make sure I give you the right installation instructions for your specific product."""
        
        return result
    
    def process_chat_with_purchase_verification(self, query: str, phone_number: str = None, first_name: str = None) -> Dict[str, Any]:
        """Enhanced chat processing with purchase verification"""
        try:
            # Extract information from query first
            extracted_info = self.extract_information_from_query(query)
            
            # If customer mentions purchase but no phone number provided, handle specially
            if extracted_info.get('mentions_purchase') and not phone_number:
                verification_result = self.handle_purchase_verification(query, extracted_info, None)
                return {
                    'success': True,
                    'response': verification_result['response'],
                    'needs_phone_number': True,
                    'phase': 'purchase_verification',
                    'extracted_info': extracted_info
                }
            
            # If we have phone number, use the regular processing with verification
            if phone_number:
                # Get or create customer session
                session = self.get_or_create_customer_session(phone_number, first_name)
                if not session:
                    return {
                        'success': False,
                        'error': 'Failed to create customer session'
                    }
                
                # Handle purchase verification if needed
                if extracted_info.get('mentions_purchase'):
                    verification_result = self.handle_purchase_verification(query, extracted_info, session.get('customer'))
                    
                    if verification_result['purchase_verified']:
                        # Add verification info to session
                        session['purchase_verification'] = verification_result['verification_result']
                        
                        # For installation help, the guidance is already included in verification_result['response']
                        if extracted_info.get('needs_installation_help'):
                            return {
                                'success': True,
                                'response': verification_result['response'],
                                'purchase_verified': True,
                                'verification_result': verification_result['verification_result'],
                                'phase': 'installation_support'
                            }
                    
                    # Return verification response
                    return {
                        'success': True,
                        'response': verification_result['response'],
                        'purchase_verified': verification_result['purchase_verified'],
                        'verification_result': verification_result.get('verification_result'),
                        'phase': 'purchase_verification'
                    }
                
                # Continue with regular conversation processing
                return self.process_chat_message(query, phone_number, first_name)
            
            # No phone number and no purchase mention - regular anonymous chat
            return {
                'success': True,
                'response': "Hello! I'm here to help you with your tile project. How can I assist you today?",
                'phase': 'greeting'
            }
            
        except Exception as e:
            logger.error(f"Error processing chat with purchase verification: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'I apologize, but I\'m experiencing some technical difficulties. Please try again.'
            }
    
    def _get_installation_guidance(self, verification_result: Dict) -> str:
        """Get specific installation guidance based on verified purchase"""
        product = None
        
        # Check exact match first
        if verification_result.get('exact_match'):
            product = verification_result['exact_match']
        # Check related products
        elif verification_result.get('customer_has_related'):
            product = verification_result['customer_has_related'][0]['purchased_product']
        
        if product:
            product_name = product['product_name'].upper()
            
            if 'ANTI-FRACTURE' in product_name or 'BACKER-LITE' in product_name or 'PERMAT' in product_name:
                return """

**Installation Steps for Anti-Fracture Mat:**

1. **Surface Preparation**: Ensure substrate is clean, flat, and structurally sound
2. **Layout**: Roll out the mat and cut to fit your area
3. **Adhesive Application**: Apply appropriate adhesive with recommended trowel
4. **Mat Installation**: Place mat into wet adhesive, removing air bubbles
5. **Seam Treatment**: Overlap seams by 2" and seal with appropriate tape
6. **Tile Installation**: Wait for cure time, then install tile using polymer-modified thinset

Would you like detailed guidance on any of these specific steps?"""
            
            elif 'HEAT MAT' in product_name or 'RADIANT' in product_name:
                return """

**Installation Steps for Electric Heat Mat:**

1. **Electrical Planning**: Ensure proper GFCI protection and electrical capacity
2. **Floor Preparation**: Clean, level substrate
3. **Layout Planning**: Plan mat placement avoiding fixtures and cabinets
4. **Mat Installation**: Secure mat with adhesive or mechanical fasteners
5. **Sensor Installation**: Install floor temperature sensor
6. **Testing**: Test system before covering with tile
7. **Tile Installation**: Cover with appropriate thinset and tile

Would you like detailed guidance on any of these specific steps?"""
        
        return """

I'll help you with the installation process! Could you let me know what specific aspect of the installation you'd like guidance on? For example:
- Surface preparation
- Product application
- Tool requirements
- Step-by-step process
- Troubleshooting"""