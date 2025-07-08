#!/usr/bin/env python3
"""
Direct API Test with Correct Key
"""

import os
import anthropic

def test_api_direct():
    """Test API directly"""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"Testing with API key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{
                "role": "user", 
                "content": "Categorize this product: Diamond Countersink Bits. Respond with just the category name from: Tool, Tile, Grout, Trim, Sealer."
            }]
        )
        
        result = response.content[0].text.strip()
        print(f"✅ API Working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    test_api_direct()