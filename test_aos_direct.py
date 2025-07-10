#!/usr/bin/env python3
"""
Test the AOS conversation engine directly
"""

import sys
sys.path.append('/Users/robertsher/Projects/tileshop_rag_prod')

from modules.simple_tile_agent import SimpleTileAgent
from modules.db_manager import DatabaseManager
from modules.rag_manager import RAGManager

def test_aos_engine_directly():
    """Test the AOS conversation engine directly"""
    
    # Initialize components
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    agent = SimpleTileAgent(db_manager, rag_manager)
    
    print("=== Testing AOS Engine Directly ===")
    print("Testing get_aos_questions tool...")
    
    # Test the get_aos_questions tool directly
    result = agent.get_aos_questions(
        project_type="kitchen",
        customer_phase="discovery",
        gathered_info="{}"
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Questions: {result.get('questions')}")
    print(f"Current Phase: {result.get('current_phase')}")
    print(f"Next Phase: {result.get('next_phase')}")
    print(f"Conversation Tips: {result.get('conversation_tips')}")
    print()
    
    # Test conversation with explicit AOS focus
    print("=== Testing Direct Agent Call ===")
    print("Query: 'hi i'm looking for kitchen floor tile'")
    print()
    
    result = agent.chat(
        message="hi i'm looking for kitchen floor tile", 
        conversation_history=[]
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Response: {result.get('response')[:300]}...")
    print(f"Tool calls: {len(result.get('tool_calls', []))}")
    for tool_call in result.get('tool_calls', []):
        print(f"  - Tool: {tool_call.get('tool')}")

if __name__ == "__main__":
    test_aos_engine_directly()