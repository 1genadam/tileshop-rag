#!/usr/bin/env python3
"""
Test the simple AI agent vs complex system
"""

import requests
import json

def test_simple_agent():
    """Test the new simple agent approach"""
    
    print("=== Testing Simple AI Agent ===\n")
    
    # Test 1: Installation query
    print("Test 1: Installation Query")
    print("Query: 'how do i install permat'")
    
    response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={"query": "how do i install permat"},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Response: {result.get('response')[:200]}...")
        if result.get('tool_calls'):
            print(f"Tools used: {[call['tool'] for call in result['tool_calls']]}")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Installation with phone number
    print("Test 2: Installation with Phone Number")
    print("Query: 'how do i install permat' with phone: 847-302-2594")
    
    response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={
            "query": "how do i install permat", 
            "phone_number": "847-302-2594"
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Response: {result.get('response')[:300]}...")
        if result.get('tool_calls'):
            print(f"Tools used: {[call['tool'] for call in result['tool_calls']]}")
    else:
        print(f"Error: {response.status_code}")

def test_complex_vs_simple():
    """Compare complex system vs simple agent"""
    
    print("\n=== COMPARISON: Complex vs Simple ===\n")
    
    query = "how do i install permat"
    phone = "847-302-2594"
    
    # Test complex system
    print("COMPLEX SYSTEM:")
    complex_response = requests.post(
        'http://localhost:8080/api/chat/unified',
        json={"query": query, "phone_number": phone},
        headers={'Content-Type': 'application/json'}
    )
    
    if complex_response.status_code == 200:
        result = complex_response.json()
        print(f"Response length: {len(result.get('response', ''))}")
        print(f"Has purchase_verified: {result.get('purchase_verified')}")
        print(f"Has verification_result: {bool(result.get('verification_result'))}")
        print(f"Phase: {result.get('phase')}")
    
    print("\nSIMPLE AGENT:")
    simple_response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={"query": query, "phone_number": phone},
        headers={'Content-Type': 'application/json'}
    )
    
    if simple_response.status_code == 200:
        result = simple_response.json()
        print(f"Response length: {len(result.get('response', ''))}")
        print(f"Tools used: {[call['tool'] for call in result.get('tool_calls', [])]}")
        print(f"Success: {result.get('success')}")

if __name__ == "__main__":
    test_simple_agent()
    test_complex_vs_simple()