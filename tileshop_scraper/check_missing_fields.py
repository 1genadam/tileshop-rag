#!/usr/bin/env python3
"""
Check for missing fields: images and collection links
"""

import subprocess
import re
import json

def check_missing_fields():
    """Check for images and collection links in the HTML"""
    
    # Get the HTML content from database
    cmd = [
        'docker', 'exec', 'n8n-postgres', 
        'psql', '-U', 'postgres', '-t', '-c',
        "SELECT raw_html FROM product_data WHERE sku = '484963';"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    html_content = result.stdout.strip()
    
    print(f"HTML content length: {len(html_content)}")
    
    # Look for image URLs
    print("\n=== SEARCHING FOR IMAGES ===")
    
    # Look for product images
    image_patterns = [
        r'<img[^>]*src="([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"[^>]*>',
        r'"url":"([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
        r'"image":"([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
        r'https://[^"]*\.scene7\.com[^"]*\.(?:jpg|jpeg|png|webp)',
    ]
    
    all_images = set()
    for pattern in image_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if 'signature' in match.lower() or 'oatmeal' in match.lower():
                all_images.add(match)
                
    print(f"Found {len(all_images)} product images:")
    for i, img in enumerate(list(all_images)[:5]):
        print(f"  {i+1}: {img}")
    
    # Look for collection links
    print("\n=== SEARCHING FOR COLLECTION LINKS ===")
    
    collection_patterns = [
        r'Available In This Collection[^<]*<[^>]*>([^<]+)',
        r'collection[^"]*"[^"]*"[^>]*>([^<]+)',
        r'href="([^"]*signature[^"]*)"[^>]*>([^<]*)',
        r'"Collection"[^}]*"href":"([^"]*)"[^}]*"text":"([^"]*)"',
    ]
    
    collection_links = []
    for pattern in collection_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple) and len(match) >= 2:
                collection_links.append({'url': match[0], 'text': match[1]})
            elif isinstance(match, str):
                collection_links.append({'text': match})
                
    print(f"Found {len(collection_links)} collection references:")
    for i, link in enumerate(collection_links[:5]):
        print(f"  {i+1}: {link}")
    
    # Look for related products or collection items
    print("\n=== SEARCHING FOR RELATED PRODUCTS ===")
    
    related_patterns = [
        r'"products":\s*\[([^\]]+)\]',
        r'"relatedProducts":\s*\[([^\]]+)\]',
        r'signature[^"]*484\d+',
    ]
    
    for pattern in related_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            print(f"Pattern '{pattern}' found {len(matches)} matches")
            if matches[0]:
                print(f"  Sample: {matches[0][:200]}...")
    
    # Look for specific collection JSON data
    print("\n=== SEARCHING FOR COLLECTION JSON ===")
    
    # Look for collection information in JSON-LD or embedded data
    collection_json_match = re.search(r'"collection"[^}]*}', html_content, re.IGNORECASE)
    if collection_json_match:
        print(f"Found collection JSON: {collection_json_match.group(0)[:200]}...")
    
    # Look for Signature collection specifically
    signature_matches = re.findall(r'.{0,50}signature.{0,50}', html_content, re.IGNORECASE)
    print(f"\nFound {len(signature_matches)} 'signature' references")
    for i, match in enumerate(signature_matches[:3]):
        clean_match = re.sub(r'<[^>]+>', ' ', match)
        clean_match = re.sub(r'\s+', ' ', clean_match).strip()
        print(f"  {i+1}: {clean_match}")

if __name__ == "__main__":
    check_missing_fields()