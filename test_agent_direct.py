#!/usr/bin/env python3
"""
Direct test of simple agent to debug phone number handling
"""

import sys
sys.path.append('/Users/robertsher/Projects/tileshop_rag_prod')

from modules.simple_tile_agent import SimpleTileAgent
from modules.db_manager import DatabaseManager
from modules.rag_manager import RAGManager

def test_agent_directly():
    """Test the agent directly without API calls"""
    
    # Initialize components
    db_manager = DatabaseManager()
    rag_manager = RAGManager()
    agent = SimpleTileAgent(db_manager, rag_manager)
    
    # Test 1: Installation query with phone number
    print("=== Direct Agent Test ===")
    print("Query: 'how do i install permat'")
    print("Phone: '847-302-2594'")
    print()
    
    result = agent.chat(
        message="how do i install permat", 
        conversation_history=[], 
        phone_number="847-302-2594"
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Response: {result.get('response')[:200]}...")
    print(f"Tool calls: {len(result.get('tool_calls', []))}")
    if result.get('tool_calls'):
        for tool_call in result.get('tool_calls', []):
            print(f"  - Tool: {tool_call.get('tool')}")
            print(f"    Found customer: {tool_call.get('result', {}).get('found', False)}")
            if tool_call.get('result', {}).get('found'):
                purchases = tool_call.get('result', {}).get('purchases', [])
                print(f"    Purchases: {len(purchases)}")
                for purchase in purchases[:2]:  # Show first 2 purchases
                    print(f"      - {purchase.get('product_name', 'Unknown')}")
    print()
    
    # Test 2: Test what the enhanced message looks like
    print("=== Enhanced Message Test ===")
    enhanced_message = "how do i install permat\n\nMy phone number is: 847-302-2594"
    print(f"Enhanced message: {repr(enhanced_message)}")
    
    result2 = agent.chat(
        message=enhanced_message, 
        conversation_history=[]
    )
    
    print(f"Success: {result2.get('success')}")
    print(f"Tool calls: {len(result2.get('tool_calls', []))}")
    if result2.get('tool_calls'):
        for tool_call in result2.get('tool_calls', []):
            print(f"  - Tool: {tool_call.get('tool')}")

if __name__ == "__main__":
    test_agent_directly()