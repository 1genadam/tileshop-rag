#!/usr/bin/env python3
"""
Debug tool to examine tab content for specifications
"""

import subprocess
import re

def check_tab_content():
    """Check what's in the specifications tab content"""
    
    # Get the specifications content from database
    cmd = [
        'docker', 'exec', 'n8n-postgres', 
        'psql', '-U', 'postgres', '-t', '-c',
        "SELECT raw_html FROM product_data WHERE sku = '484963';"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    html_content = result.stdout.strip()
    
    print(f"HTML content length: {len(html_content)}")
    
    # Look for specification-related content
    spec_keywords = [
        'approximate size', 'thickness', 'material type', 'ceramic',
        'dimensions', 'box quantity', 'box weight', 'frost resistance',
        'country of origin', 'applications', 'surface texture'
    ]
    
    print("\n=== SEARCHING FOR SPECIFICATION KEYWORDS ===")
    for keyword in spec_keywords:
        # Search case-insensitive
        pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            print(f"\n{keyword.upper()}:")
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                clean_match = re.sub(r'<[^>]+>', '', match)
                print(f"  {i+1}: ...{clean_match}...")
    
    # Look for table structures that might contain specs
    print("\n=== LOOKING FOR TABLE STRUCTURES ===")
    table_patterns = [
        r'<table[^>]*>.*?</table>',
        r'<div[^>]*class="[^"]*spec[^"]*"[^>]*>.*?</div>',
        r'<section[^>]*>.*?</section>',
    ]
    
    for pattern in table_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"Found {len(matches)} {pattern} structures")
            # Show a sample
            sample = matches[0][:300] if matches else ""
            clean_sample = re.sub(r'<[^>]+>', ' ', sample)
            clean_sample = re.sub(r'\s+', ' ', clean_sample).strip()
            if any(keyword in clean_sample.lower() for keyword in spec_keywords):
                print(f"  Sample with specs: {clean_sample}...")

if __name__ == "__main__":
    check_tab_content()