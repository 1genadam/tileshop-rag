#!/usr/bin/env python3
"""
Debug validation logic
"""

import sys
sys.path.append('/Users/robertsher/Projects/tileshop_rag_prod')

from modules.simple_tile_agent import SimpleTileAgent
from modules.db_manager import DatabaseManager
from modules.rag_manager import RAGManager

def test_validation():
    """Debug validation requirements"""
    
    # Initialize components
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    agent = SimpleTileAgent(db_manager, rag_manager)
    
    # Test conversation history
    conversation_history = [
        {"role": "user", "content": "hi i am looking for kitchen floor tile"},
        {"role": "assistant", "content": "Hi! I am Alex from The Tile Shop. May I have your name?"},
        {"role": "user", "content": "my name is Sarah and my phone is 847-302-2594"},
        {"role": "assistant", "content": "Hi Sarah! Let me check your purchase history."},
        {"role": "user", "content": "the kitchen is 8 feet by 10 feet, we have black countertops and white cabinets"},
        {"role": "assistant", "content": "Thanks Sarah! Those dimensions are perfect."},
        {"role": "user", "content": "we have a contractor, our budget is around $1000, we want to start next week"}
    ]
    
    print("=== DEBUGGING VALIDATION LOGIC ===")
    
    # Test validation
    validation = agent.validate_aos_requirements(conversation_history, "search_products")
    
    print(f"Validation result: {validation}")
    print()
    
    # Test individual requirement checks
    conversation_text = ""
    for msg in conversation_history:
        if msg.get("role") == "user":
            conversation_text += f" {msg.get('content', '')}"
    
    print(f"Full conversation text: {conversation_text}")
    print()
    
    # Check each requirement
    name_check = agent._check_name_collected(conversation_text.lower())
    dimensions_check = agent._check_dimensions_collected(conversation_text.lower())
    budget_check = agent._check_budget_collected(conversation_text.lower())
    installation_check = agent._check_installation_method_collected(conversation_text.lower())
    timeline_check = agent._check_timeline_collected(conversation_text.lower())
    
    print("INDIVIDUAL REQUIREMENT CHECKS:")
    print(f"Name collected: {name_check}")
    print(f"Dimensions collected: {dimensions_check}")
    print(f"Budget collected: {budget_check}")
    print(f"Installation method collected: {installation_check}")
    print(f"Timeline collected: {timeline_check}")

if __name__ == "__main__":
    test_validation()