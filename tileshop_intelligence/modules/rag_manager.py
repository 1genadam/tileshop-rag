#!/usr/bin/env python3
"""
RAG Manager - Manages RAG system operations
"""

import sys
import os
import logging
from typing import Dict, List, Any, Optional

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_rag import SimpleTileshopRAG
except ImportError:
    SimpleTileshopRAG = None

logger = logging.getLogger(__name__)

class RAGManager:
    """Manages RAG system operations and chat interface"""
    
    def __init__(self):
        self.rag_system = None
        self.conversation_history = []
        self.max_history = 50
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize RAG system"""
        try:
            if SimpleTileshopRAG:
                self.rag_system = SimpleTileshopRAG()
                logger.info("RAG system initialized successfully")
            else:
                logger.warning("SimpleTileshopRAG not available")
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
            # Get response from RAG system
            response = self.rag_system.chat(query.strip())
            
            # Add to conversation history
            self._add_to_history(user_id, query, response)
            
            return {
                'success': True,
                'query': query,
                'response': response,
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