#!/usr/bin/env python3
"""
RAG Manager - Manages RAG system operations
"""

import sys
import os
import logging
import re
import json
import glob
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from .pdf_processor import PDFProcessor
    PDF_KNOWLEDGE_BASE_AVAILABLE = True
except ImportError:
    PDFProcessor = None
    PDF_KNOWLEDGE_BASE_AVAILABLE = False

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_rag import SimpleTileShopRAG
except ImportError:
    SimpleTileShopRAG = None

logger = logging.getLogger(__name__)

class RAGManager:
    """Manages RAG system operations and chat interface"""
    
    def __init__(self):
        self.rag_system = None
        self.conversation_history = []
        self.max_history = 50
        self.knowledge_base = {}
        self.pdf_processor = None
        self._initialize_rag()
        self._load_knowledge_base()
        self._initialize_pdf_knowledge_base()
    
    def _initialize_rag(self):
        """Initialize RAG system"""
        try:
            if SimpleTileShopRAG:
                self.rag_system = SimpleTileShopRAG()
                logger.info("RAG system initialized successfully")
            else:
                logger.warning("SimpleTileShopRAG not available")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.rag_system = None
    
    def is_available(self) -> bool:
        """Check if RAG system is available"""
        return self.rag_system is not None
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync product data to vector database"""
        if not self.rag_system:
            return {
                'success': False,
                'error': 'RAG system not available'
            }
        
        try:
            success = self.rag_system.sync_data()
            
            if success:
                return {
                    'success': True,
                    'message': 'Product data synced to vector database successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to sync data - check logs for details'
                }
                
        except Exception as e:
            logger.error(f"Error syncing RAG data: {e}")
            return {
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }
    
    def chat(self, query: str, user_id: str = 'default') -> Dict[str, Any]:
        """Process chat query and return response"""
        if not self.rag_system:
            return {
                'success': False,
                'error': 'RAG system not available',
                'response': 'Sorry, the AI assistant is currently unavailable. Please check system status.'
            }
        
        if not query or not query.strip():
            return {
                'success': False,
                'error': 'Empty query',
                'response': 'Please ask me something about tiles or products.'
            }
        
        try:
            # Check if query might benefit from PDF knowledge base
            pdf_results = []
            query_lower = query.lower()
            
            # Keywords that suggest PDF knowledge base search
            pdf_keywords = [
                'install', 'installation', 'how to install',
                'care', 'clean', 'cleaning', 'maintenance', 'maintain',
                'warranty', 'guarantee', 'protection',
                'specification', 'specs', 'technical', 'dimensions',
                'guide', 'instructions', 'manual', 'steps'
            ]
            
            if any(keyword in query_lower for keyword in pdf_keywords) and self.pdf_processor:
                # Determine category based on query
                category = None
                if any(word in query_lower for word in ['install', 'installation']):
                    category = 'installation_guide'
                elif any(word in query_lower for word in ['care', 'clean', 'maintenance']):
                    category = 'care_instructions'
                elif any(word in query_lower for word in ['warranty', 'guarantee']):
                    category = 'warranty_info'
                elif any(word in query_lower for word in ['spec', 'technical', 'dimension']):
                    category = 'specification_sheet'
                
                pdf_results = self.search_pdf_knowledge_base(query, category)
            
            # Get response from RAG system
            response = self.rag_system.chat(query.strip())
            
            # Enhance response with PDF knowledge if available
            if pdf_results:
                enhanced_response = self._enhance_response_with_pdf_knowledge(response, pdf_results)
                response = enhanced_response
            
            # Add to conversation history
            self._add_to_history(user_id, query, response)
            
            return {
                'success': True,
                'query': query,
                'response': response,
                'pdf_sources': len(pdf_results),
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error processing your request. Please try again.'
            }
    
    def search_products(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search products directly (for API use)"""
        if not self.rag_system:
            return {
                'success': False,
                'error': 'RAG system not available',
                'results': []
            }
        
        try:
            results = self.rag_system.search_products(query, limit)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def get_conversation_history(self, user_id: str = 'default', limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for user"""
        user_history = [
            msg for msg in self.conversation_history 
            if msg.get('user_id') == user_id
        ]
        
        return user_history[-limit:] if user_history else []
    
    def clear_conversation(self, user_id: str = 'default') -> Dict[str, Any]:
        """Clear conversation history for user"""
        original_count = len(self.conversation_history)
        
        self.conversation_history = [
            msg for msg in self.conversation_history 
            if msg.get('user_id') != user_id
        ]
        
        cleared_count = original_count - len(self.conversation_history)
        
        return {
            'success': True,
            'cleared_messages': cleared_count,
            'message': f'Cleared {cleared_count} messages from conversation history'
        }
    
    def get_suggested_queries(self) -> List[str]:
        """Get suggested queries for the chat interface"""
        return [
            "Show me ceramic subway tiles under $100",
            "What travertine tiles do you have?",
            "Show me bathroom wall tiles",
            "What are the most expensive tiles?",
            "Find tiles with matte finish",
            "Show me 12 inch tiles",
            "What colors are available in porcelain tiles?",
            "Show me tiles for kitchen backsplash"
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get RAG system status"""
        status = {
            'rag_available': self.is_available(),
            'conversation_count': len(self.conversation_history),
            'max_history': self.max_history
        }
        
        if self.rag_system:
            try:
                # Test database connection
                test_result = self.rag_system.search_products("test", 1)
                status['database_connected'] = True
                status['sample_product_count'] = len(test_result)
            except Exception as e:
                status['database_connected'] = False
                status['database_error'] = str(e)
        else:
            status['database_connected'] = False
            status['error'] = 'RAG system not initialized'
        
        return status
    
    def _add_to_history(self, user_id: str, query: str, response: str):
        """Add conversation to history"""
        self.conversation_history.append({
            'user_id': user_id,
            'timestamp': self._get_timestamp(),
            'query': query,
            'response': response
        })
        
        # Keep only recent conversations
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def export_conversation(self, user_id: str = 'default', format: str = 'json') -> Dict[str, Any]:
        """Export conversation history"""
        try:
            history = self.get_conversation_history(user_id, limit=1000)
            
            if format.lower() == 'json':
                import json
                content = json.dumps({
                    'user_id': user_id,
                    'export_date': self._get_timestamp(),
                    'message_count': len(history),
                    'conversation': history
                }, indent=2)
                
                return {
                    'success': True,
                    'content': content,
                    'filename': f'chat_history_{user_id}_{self._get_timestamp()[:10]}.json',
                    'content_type': 'application/json'
                }
            
            elif format.lower() == 'txt':
                lines = [f"Chat History for {user_id}", "=" * 50, ""]
                
                for msg in history:
                    lines.append(f"[{msg['timestamp']}]")
                    lines.append(f"You: {msg['query']}")
                    lines.append(f"Bot: {msg['response']}")
                    lines.append("")
                
                content = "\n".join(lines)
                
                return {
                    'success': True,
                    'content': content,
                    'filename': f'chat_history_{user_id}_{self._get_timestamp()[:10]}.txt',
                    'content_type': 'text/plain'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported export format: {format}'
                }
                
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular queries from history"""
        try:
            query_counts = {}
            
            for msg in self.conversation_history:
                query = msg['query'].lower().strip()
                query_counts[query] = query_counts.get(query, 0) + 1
            
            # Sort by count and return top queries
            popular = sorted(
                query_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            return [
                {
                    'query': query,
                    'count': count,
                    'percentage': round((count / len(self.conversation_history)) * 100, 1)
                }
                for query, count in popular
            ]
            
        except Exception as e:
            logger.error(f"Error getting popular queries: {e}")
            return []
    
    def _load_knowledge_base(self):
        """Load knowledge base files"""
        try:
            knowledge_dir = Path(__file__).parent.parent / "knowledge_base"
            if not knowledge_dir.exists():
                logger.warning(f"Knowledge base directory not found: {knowledge_dir}")
                return
            
            # Load all markdown files in knowledge base
            for md_file in knowledge_dir.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Store content by filename (without extension)
                    key = md_file.stem
                    self.knowledge_base[key] = {
                        'content': content,
                        'path': str(md_file),
                        'title': self._extract_title(content)
                    }
                    
                except Exception as e:
                    logger.error(f"Error loading knowledge file {md_file}: {e}")
            
            logger.info(f"Loaded {len(self.knowledge_base)} knowledge base files")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
    
    def _initialize_pdf_knowledge_base(self):
        """Initialize PDF knowledge base processor"""
        try:
            if PDF_KNOWLEDGE_BASE_AVAILABLE:
                self.pdf_processor = PDFProcessor()
                logger.info("PDF knowledge base processor initialized")
            else:
                logger.warning("PDF knowledge base not available - install PyPDF2 and pdfplumber")
        except Exception as e:
            logger.error(f"Failed to initialize PDF knowledge base: {e}")
    
    def search_pdf_knowledge_base(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Search PDF knowledge base for relevant content"""
        if not self.pdf_processor:
            return []
        
        try:
            results = self.pdf_processor.search_knowledge_base(query, category)
            return results
        except Exception as e:
            logger.error(f"Error searching PDF knowledge base: {e}")
            return []
    
    def get_pdf_knowledge_summary(self) -> Dict:
        """Get summary of PDF knowledge base"""
        if not self.pdf_processor:
            return {'total_documents': 0, 'categories': {}}
        
        try:
            return self.pdf_processor.get_knowledge_base_summary()
        except Exception as e:
            logger.error(f"Error getting PDF knowledge summary: {e}")
            return {'total_documents': 0, 'categories': {}}
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "Unknown"
    
    def calculate_tile_needs(self, room_length: float, room_width: float, 
                           tile_coverage_per_box: float, waste_factor: float = 0.15,
                           deductions: List[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate tile needs for a room"""
        try:
            # Calculate base area
            base_area = room_length * room_width
            
            # Subtract deductions (cabinets, etc.)
            total_deductions = 0
            if deductions:
                for deduction in deductions:
                    deduct_area = deduction.get('length', 0) * deduction.get('width', 0)
                    total_deductions += deduct_area
            
            net_area = base_area - total_deductions
            
            # Add waste factor
            area_with_waste = net_area * (1 + waste_factor)
            
            # Calculate boxes needed (always round up)
            boxes_needed = int(-(-area_with_waste // tile_coverage_per_box))  # Ceiling division
            
            # Calculate grout needs based on tile size
            grout_bags = self._calculate_grout_needs(net_area, room_length, room_width)
            
            return {
                'success': True,
                'calculations': {
                    'room_dimensions': f"{room_length} ft × {room_width} ft",
                    'base_area': round(base_area, 2),
                    'deductions': round(total_deductions, 2),
                    'net_area': round(net_area, 2),
                    'waste_factor_percent': int(waste_factor * 100),
                    'area_with_waste': round(area_with_waste, 2),
                    'tile_coverage_per_box': tile_coverage_per_box,
                    'boxes_needed': boxes_needed,
                    'grout_bags_needed': grout_bags,
                    'total_tile_coverage': boxes_needed * tile_coverage_per_box
                },
                'recommendations': self._get_installation_recommendations(net_area, boxes_needed)
            }
            
        except Exception as e:
            logger.error(f"Error calculating tile needs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_grout_needs(self, area: float, length: float, width: float) -> int:
        """Calculate grout bag needs based on area"""
        # Standard sanded grout covers 105-115 sq ft per 25lb bag for subway tile
        # Adjust based on area size
        if area <= 50:
            return 1  # Minimum 1 bag
        elif area <= 100:
            return 2  # 2 bags for medium rooms
        else:
            return int(-(-area // 100)) + 1  # 1 bag per 100 sq ft + buffer
    
    def _get_installation_recommendations(self, area: float, tile_boxes: int) -> Dict[str, Any]:
        """Get installation material recommendations"""
        base_cost = tile_boxes * 50  # Estimate $50/box average
        
        # Essential materials
        essentials = {
            'grout_bags': max(1, int(-(-area // 100))),  # 1 bag per 100 sq ft minimum
            'thinset_bags': max(1, int(-(-area // 100))),  # 1 bag per 100 sq ft minimum  
            'sealer_quarts': max(1, int(-(-area // 150))),  # 1 quart per 150 sq ft
            'basic_tools': 1  # Tool package
        }
        
        # Premium upgrades
        premium_options = []
        if area > 50:  # Larger rooms
            premium_options.append("Anti-fracture membrane for enhanced durability")
            premium_options.append("Heated floor system (eliminates membrane need)")
        
        premium_options.append("Premium grout sealer for enhanced protection")
        premium_options.append("Professional-grade tools for better results")
        
        return {
            'essentials': essentials,
            'estimated_base_cost': base_cost,
            'premium_options': premium_options,
            'return_policy_note': "Order complete boxes only - no partial box returns after 60 days"
        }
    
    def check_dcof_requirements(self, application: str, is_wet_area: bool = False) -> Dict[str, Any]:
        """Check DCOF requirements for specific applications"""
        try:
            # DCOF requirements based on application
            dcof_requirements = {
                'bathroom_floor': {'min_dcof': 0.60, 'class': 3, 'wet_testing': True},
                'shower_floor': {'min_dcof': 0.70, 'class': 3, 'wet_testing': True},
                'kitchen_floor': {'min_dcof': 0.42, 'class': 2, 'wet_testing': False},
                'commercial_kitchen': {'min_dcof': 0.60, 'class': 3, 'wet_testing': True},
                'pool_deck': {'min_dcof': 0.60, 'class': 3, 'wet_testing': True},
                'living_area': {'min_dcof': 0.42, 'class': 1, 'wet_testing': False},
                'staircase': {'min_dcof': 0.42, 'class': 2, 'wet_testing': False}
            }
            
            app_lower = application.lower()
            requirement = None
            
            # Match application to requirements
            for key, req in dcof_requirements.items():
                if key in app_lower or any(word in app_lower for word in key.split('_')):
                    requirement = req.copy()
                    requirement['application'] = key
                    break
            
            if not requirement:
                # Default based on wet area
                requirement = {
                    'min_dcof': 0.60 if is_wet_area else 0.42,
                    'class': 3 if is_wet_area else 1,
                    'wet_testing': is_wet_area,
                    'application': 'general'
                }
            
            # Add recommendations
            recommendations = []
            if requirement['min_dcof'] >= 0.60:
                recommendations.extend([
                    "Look for matte or textured finishes",
                    "Avoid glossy or polished tiles",
                    "Consider anti-slip surface treatments",
                    "Ensure tiles meet DCOF requirements when wet"
                ])
            
            if requirement['wet_testing']:
                recommendations.append("Verify DCOF rating was tested under wet conditions")
            
            return {
                'success': True,
                'application': application,
                'requirements': requirement,
                'recommendations': recommendations,
                'compliance_note': "Consult with Tile Shop representative for specific product DCOF ratings"
            }
            
        except Exception as e:
            logger.error(f"Error checking DCOF requirements: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def enhanced_chat(self, query: str, user_id: str = 'default') -> Dict[str, Any]:
        """Enhanced chat with calculator and knowledge base integration"""
        try:
            # Check for calculator-related queries
            calc_result = self._check_calculator_query(query)
            if calc_result:
                self._add_to_history(user_id, query, calc_result['response'])
                return {
                    'success': True,
                    'query': query,
                    'response': calc_result['response'],
                    'calculator_data': calc_result.get('data'),
                    'timestamp': self._get_timestamp(),
                    'type': 'calculator'
                }
            
            # Check for DCOF/compliance queries
            dcof_result = self._check_dcof_query(query)
            if dcof_result:
                self._add_to_history(user_id, query, dcof_result['response'])
                return {
                    'success': True,
                    'query': query,
                    'response': dcof_result['response'],
                    'dcof_data': dcof_result.get('data'),
                    'timestamp': self._get_timestamp(),
                    'type': 'dcof_compliance'
                }
            
            # Check knowledge base for relevant information
            kb_context = self._search_knowledge_base(query)
            
            # Use regular RAG system with knowledge base context
            if self.rag_system:
                if kb_context:
                    enhanced_query = f"{query}\n\nRelevant information:\n{kb_context[:500]}..."
                    response = self.rag_system.chat(enhanced_query)
                else:
                    response = self.rag_system.chat(query)
                
                self._add_to_history(user_id, query, response)
                return {
                    'success': True,
                    'query': query,
                    'response': response,
                    'knowledge_context': kb_context is not None,
                    'timestamp': self._get_timestamp(),
                    'type': 'enhanced_rag'
                }
            else:
                # Fallback to knowledge base only
                if kb_context:
                    response = f"Based on our installation guides:\n\n{kb_context[:800]}..."
                    self._add_to_history(user_id, query, response)
                    return {
                        'success': True,
                        'query': query,
                        'response': response,
                        'timestamp': self._get_timestamp(),
                        'type': 'knowledge_base'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No relevant information found',
                        'response': 'Sorry, I couldn\'t find information about that. Could you be more specific?'
                    }
                    
        except Exception as e:
            logger.error(f"Error in enhanced chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error. Please try again.'
            }
    
    def _check_calculator_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if query is asking for tile calculations"""
        calc_keywords = ['calculate', 'how much', 'how many', 'room size', 'square feet', 'boxes needed']
        if not any(keyword in query.lower() for keyword in calc_keywords):
            return None
        
        # Extract dimensions if provided
        dimension_pattern = r'(\d+(?:\.\d+)?)\s*(?:ft|feet|foot)?\s*(?:x|by|\*)\s*(\d+(?:\.\d+)?)\s*(?:ft|feet|foot)?'
        match = re.search(dimension_pattern, query.lower())
        
        if match:
            length = float(match.group(1))
            width = float(match.group(2))
            
            # Use default tile coverage (can be enhanced to detect tile type)
            default_coverage = 10.76  # Subway tile coverage
            
            result = self.calculate_tile_needs(length, width, default_coverage)
            
            if result['success']:
                calc_data = result['calculations']
                response = f"""**Tile Calculator Results**

**Room**: {calc_data['room_dimensions']} = {calc_data['net_area']} sq ft
**With {calc_data['waste_factor_percent']}% waste factor**: {calc_data['area_with_waste']} sq ft needed
**Boxes required**: {calc_data['boxes_needed']} boxes (at {default_coverage} sq ft per box)

**Installation Materials Needed**:
- Grout: {calc_data['grout_bags_needed']} bags (25 lb sanded)
- Thinset: {calc_data['grout_bags_needed']} bags (50 lb)
- Sealer: 1 quart

**Important**: We can only accept returns of complete, unopened boxes within 60 days. Always round up to complete boxes.

Would you like me to help you select specific tiles or provide installation guidance?"""
                
                return {
                    'response': response,
                    'data': calc_data
                }
        
        # If no dimensions found, ask for them
        return {
            'response': """I'd be happy to calculate your tile needs! Please provide:

1. **Room dimensions** (length × width in feet)
2. **Tile type** you're considering (I'll look up the coverage per box)
3. **Any areas to exclude** (cabinets, fixtures, etc.)

Example: "I have a 10 ft by 12 ft bathroom, minus a 2x4 ft vanity"

I'll calculate the exact number of boxes needed plus installation materials!""",
            'data': None
        }
    
    def _check_dcof_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Check if query is asking about DCOF ratings or slip resistance"""
        dcof_keywords = ['dcof', 'slip resistant', 'slip resistance', 'friction', 'safety', 'bathroom safe', 'pool safe']
        if not any(keyword in query.lower() for keyword in dcof_keywords):
            return None
        
        # Determine application from query
        applications = {
            'bathroom': ['bathroom', 'shower', 'bath'],
            'kitchen': ['kitchen', 'cooking'],
            'pool': ['pool', 'deck', 'swimming'],
            'commercial': ['commercial', 'restaurant', 'business'],
            'stair': ['stair', 'steps']
        }
        
        detected_app = 'general'
        for app, keywords in applications.items():
            if any(kw in query.lower() for kw in keywords):
                detected_app = app
                break
        
        is_wet = any(word in query.lower() for word in ['shower', 'bathroom', 'pool', 'wet'])
        
        result = self.check_dcof_requirements(detected_app, is_wet)
        
        if result['success']:
            req = result['requirements']
            response = f"""**DCOF Requirements for {detected_app.title()} Application**

**Minimum DCOF Rating**: {req['min_dcof']} ({'wet' if req['wet_testing'] else 'dry'} testing)
**Safety Class**: Class {req['class']}

**Recommendations**:
"""
            for rec in result['recommendations']:
                response += f"- {rec}\n"
            
            response += f"""
**Compliance Note**: {result['compliance_note']}

**What This Means**: DCOF measures slip resistance. Higher numbers = better grip. Wet areas need higher ratings for safety.

Would you like me to help you find tiles that meet these requirements?"""
            
            return {
                'response': response,
                'data': result
            }
        
        return None
    
    def _search_knowledge_base(self, query: str) -> Optional[str]:
        """Search knowledge base for relevant information"""
        if not self.knowledge_base:
            return None
        
        query_lower = query.lower()
        relevant_content = []
        
        # Search for relevant knowledge base entries
        for key, kb_item in self.knowledge_base.items():
            content = kb_item['content'].lower()
            
            # Simple keyword matching - can be enhanced with better scoring
            if any(word in content for word in query_lower.split() if len(word) > 3):
                relevant_content.append({
                    'title': kb_item['title'],
                    'content': kb_item['content'][:500],  # First 500 chars
                    'relevance': self._calculate_relevance(query_lower, content)
                })
        
        if relevant_content:
            # Sort by relevance and return top result
            relevant_content.sort(key=lambda x: x['relevance'], reverse=True)
            best_match = relevant_content[0]
            return f"**{best_match['title']}**\n\n{best_match['content']}"
        
        return None
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content"""
        query_words = set(query.split())
        content_words = set(content.split())
        
        # Simple Jaccard similarity
        intersection = query_words.intersection(content_words)
        union = query_words.union(content_words)
        
        return len(intersection) / len(union) if union else 0
    
    def _enhance_response_with_pdf_knowledge(self, response: str, pdf_results: List[Dict]) -> str:
        """Enhance RAG response with relevant PDF knowledge base content"""
        if not pdf_results:
            return response
        
        # Create enhanced response with PDF sources
        enhanced_response = response + "\n\n**📚 Additional Resources from Installation Guides:**\n\n"
        
        for i, result in enumerate(pdf_results[:3], 1):  # Limit to top 3 results
            enhanced_response += f"**{i}. {result['title']}** ({result['category']})\n"
            
            # Add matched sections
            if result.get('matched_sections'):
                for section in result['matched_sections'][:2]:  # Top 2 sections per document
                    section_content = section.get('content', '')[:300]  # First 300 chars
                    if section_content:
                        enhanced_response += f"• {section.get('header', 'Section')}: {section_content}...\n"
            
            enhanced_response += "\n"
        
        enhanced_response += "_💡 For complete installation guides and detailed instructions, refer to the full documents above._"
        
        return enhanced_response