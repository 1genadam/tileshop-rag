#!/usr/bin/env python3
"""
Test specific field extraction for SKU 683861
"""

from curl_scraper import get_page_with_curl
import re
import json

def test_field_extraction():
    url = 'https://www.tileshop.com/products/morris-&-co-pure-net-brick-porcelain-wall-and-floor-tile-13-x-13-in-683861'
    html = get_page_with_curl(url)
    
    print('🔍 Testing specific field extraction for SKU 683861...')
    print('=' * 60)
    
    # 1. Test price per sqft extraction
    print('📍 1. Price per sqft search:')
    price_sqft_patterns = [
        r'\$(\d+\.\d+)(?:/|\s+per\s+)(?:sq\.?\s*ft|square\s+foot)',
        r'price.*?(\d+\.\d+).*?sq\.?\s*ft',
        r'(\d+\.\d+).*?\/\s*sq\.?\s*ft',
        r'"price":\s*"(\d+\.\d+)".*?"unit":\s*"sqft"',
        r'"pricePerSqFt":\s*"?(\d+\.\d+)"?'
    ]
    
    found_price = False
    for i, pattern in enumerate(price_sqft_patterns):
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f'  ✓ Pattern {i+1} found: ${matches[0]}/sq ft')
            found_price = True
            break
    
    if not found_price:
        print('  ❌ Price per sqft not found with patterns')
        # Check if any pricing info exists
        if '$12.99' in html:
            print('  📍 Found literal $12.99 in HTML - need better pattern')
        
    # 2. Test color extraction
    print('\n📍 2. Color search:')
    color_patterns = [
        r'"color":\s*"([^"]+)"',
        r'Color:\s*([^<\n,]+)',
        r'class="color[^"]*"[^>]*>([^<]+)',
        r'data-color="([^"]+)"',
        r'Beige[,\s]*Brown'  # Specific for this product
    ]
    
    found_color = False
    for i, pattern in enumerate(color_patterns):
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f'  ✓ Pattern {i+1} found: {matches[0]}')
            found_color = True
            break
    
    if not found_color:
        if 'Beige' in html and 'Brown' in html:
            print('  📍 Found "Beige" and "Brown" separately - need combination pattern')
        else:
            print('  ❌ Color not found')
    
    # 3. Test resources/PDF extraction
    print('\n📍 3. Resources/PDF search:')
    pdf_patterns = [
        r'href="([^"]*\.pdf[^"]*)"',
        r'href=\'([^\']*\.pdf[^\']*)\'',
        r'Resources.*?href="([^"]+)"',
        r'Installation.*?href="([^"]+\.pdf)"',
        r'Care.*?href="([^"]+\.pdf)"'
    ]
    
    found_pdf = False
    for i, pattern in enumerate(pdf_patterns):
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f'  ✓ Pattern {i+1} found PDF: {matches[0]}')
            found_pdf = True
        
    if not found_pdf:
        print('  ❌ PDF resources not found')
        if 'Installation' in html:
            print('  📍 Found "Installation" text - PDFs may be dynamically loaded')
    
    # 4. Test product category extraction
    print('\n📍 4. Product category search:')
    category_patterns = [
        r'"productType":\s*"([^"]+)"',
        r'"category":\s*"([^"]+)"',
        r'Wall\s+and\s+Floor\s+Tile',
        r'breadcrumb.*?tile',
        r'Tile\s*Shop.*?([^<\n]+tile[^<\n]*)'
    ]
    
    found_category = False
    for i, pattern in enumerate(category_patterns):
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f'  ✓ Pattern {i+1} found: {matches[0]}')
            found_category = True
    
    if not found_category:
        if 'Wall and Floor Tile' in html:
            print('  ✓ Found "Wall and Floor Tile" - category should be "Tile"')
        else:
            print('  ❌ Category not found')
    
    # 5. Check JSON-LD data specifically
    print('\n📍 5. JSON-LD structured data search:')
    json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    json_matches = re.findall(json_ld_pattern, html, re.DOTALL | re.IGNORECASE)
    
    for i, json_str in enumerate(json_matches):
        try:
            data = json.loads(json_str.strip())
            print(f'  ✓ JSON-LD {i+1} parsed successfully')
            
            # Check for price info
            if 'offers' in data:
                offers = data['offers']
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = offers.get('price')
                if price:
                    print(f'    💰 Price found: ${price}')
            
            # Check for color
            if 'color' in data:
                print(f'    🎨 Color: {data["color"]}')
            
            # Check for category
            if 'category' in data:
                print(f'    📂 Category: {data["category"]}')
                
        except json.JSONDecodeError:
            print(f'  ❌ JSON-LD {i+1} parse failed')
    
    print('\n' + '=' * 60)
    print('🎯 EXTRACTION ANALYSIS COMPLETE')

if __name__ == "__main__":
    test_field_extraction()