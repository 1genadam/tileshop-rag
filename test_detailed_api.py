#!/usr/bin/env python3
"""
Detailed test to debug the API vs direct test difference
"""

import requests
import json

def test_api_detailed():
    """Test the API with detailed logging"""
    
    print("=== Testing API with Phone Number ===")
    
    response = requests.post(
        'http://localhost:8080/api/chat/simple',
        json={
            "query": "how do i install permat", 
            "phone_number": "847-302-2594"
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Response length: {len(result.get('response', ''))}")
        print(f"Full response: {result.get('response')}")
        print(f"Tool calls: {len(result.get('tool_calls', []))}")
        
        if result.get('tool_calls'):
            print("Tool calls found:")
            for i, tool_call in enumerate(result.get('tool_calls', [])):
                print(f"  {i+1}. Tool: {tool_call.get('tool')}")
                print(f"     Result: {tool_call.get('result', {})}")
        else:
            print("No tool calls found!")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api_detailed()