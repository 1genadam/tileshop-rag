#!/usr/bin/env python3
"""
Test the enhanced AOS-focused SimpleTileAgent
"""

import requests
import json

def test_kitchen_query():
    """Test kitchen floor tile query for AOS response"""
    
    print("=== Testing Enhanced AOS Agent ===")
    print("Query: 'hi i'm looking for kitchen floor tile'")
    print()
    
    response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={"query": "hi i'm looking for kitchen floor tile"},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS!")
        print(f"Response: {result.get('response')}")
        print()
        print(f"Tool calls: {len(result.get('tool_calls', []))}")
        for tool_call in result.get('tool_calls', []):
            print(f"  - Tool: {tool_call.get('tool')}")
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)

def test_follow_up():
    """Test follow-up conversation with phone number"""
    
    print("\n=== Testing Follow-up with Phone ===")
    print("Query: 'my phone number is 555-123-4567'")
    print()
    
    # Simulate conversation history
    conversation_history = [
        {"role": "user", "content": "hi i'm looking for kitchen floor tile"},
        {"role": "assistant", "content": "I'd love to help you find the perfect kitchen floor tile! To save our conversation for future reference and check if we have anything in stock for you, what phone number should I save this under?"}
    ]
    
    response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={
            "query": "my phone number is 555-123-4567",
            "conversation_history": conversation_history
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS!")
        print(f"Response: {result.get('response')}")
        print()
        print(f"Tool calls: {len(result.get('tool_calls', []))}")
        for tool_call in result.get('tool_calls', []):
            print(f"  - Tool: {tool_call.get('tool')}")
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_kitchen_query()
    test_follow_up()