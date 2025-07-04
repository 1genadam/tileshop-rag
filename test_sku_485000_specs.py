#!/usr/bin/env python3
"""
Test SKU 485000 specifications tab for price per sqft display
"""

import subprocess
import re

def test_specifications_tab():
    print("🔍 Testing SKU 485000 Specifications Tab for Price Per Sqft")
    print("=" * 60)
    
    url = 'https://www.tileshop.com/products/laura-park-bespoke-white-ceramic-wall-tile-256-x-10-in-485000#specifications'
    
    try:
        result = subprocess.run([
            'curl', '-s', '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            url
        ], capture_output=True, text=True)
        
        html = result.stdout
        
        print(f"✅ Successfully fetched specifications tab")
        print(f"📄 Content length: {len(html)} characters")
        
        # Look for price per sqft patterns
        price_patterns = [
            r'\$([0-9]+\.?[0-9]*)\s*/\s*[Ss]q\s*[Ff]t',
            r'\$([0-9]+\.?[0-9]*)\s*[Pp]er\s*[Ss]q\s*[Ff]t',
            r'([0-9]+\.99)\s*/\s*[Ss]q\s*[Ff]t',
            r'Price\s*per\s*[Ss]q\s*[Ff]t[^0-9]*\$([0-9]+\.?[0-9]*)',
        ]
        
        found_any = False
        for i, pattern in enumerate(price_patterns):
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f'💰 Pattern {i+1} found: {matches}')
                found_any = True
        
        # Look specifically for 12.99
        twelve_ninety_nine = re.findall(r'12\.99', html)
        if twelve_ninety_nine:
            print(f'🎯 Found 12.99 mentions: {len(twelve_ninety_nine)} times')
            
            # Look for context around 12.99
            context_pattern = r'.{0,80}12\.99.{0,80}'
            contexts = re.findall(context_pattern, html, re.IGNORECASE | re.DOTALL)
            for i, context in enumerate(contexts[:3]):
                clean_context = ' '.join(context.strip().split())
                print(f'📝 Context {i+1}: {clean_context}')
        
        # Look for specifications structure
        if re.search(r'specifications', html, re.IGNORECASE):
            print("✅ Found specifications section in HTML")
        
        if not found_any and not twelve_ninety_nine:
            print("❌ No price per sqft or 12.99 found in specifications tab")
            
            # Sample the HTML to see what we're working with
            print("\n📋 Sample HTML content (first 500 chars):")
            print(html[:500] + "..." if len(html) > 500 else html)
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_specifications_tab()