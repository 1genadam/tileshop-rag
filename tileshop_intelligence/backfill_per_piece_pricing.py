#!/usr/bin/env python3
"""
Backfill Per-Piece Pricing Script
Finds products without price_per_sqft and populates price_per_piece field
"""

import psycopg2
import requests
import re
import time
import json

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"
DB_CONFIG = {
    'host': '127.0.0.1',  # Use IPv4 instead of localhost
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'  # Use correct password
}

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_products_without_sqft_price():
    """Get products that have no price_per_sqft (likely per-piece products)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT url, sku, title, price_per_box, price_per_piece
        FROM product_data 
        WHERE price_per_sqft IS NULL 
        AND price_per_box IS NOT NULL
        ORDER BY sku
        LIMIT 5;
    """)
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return products

def fetch_page_html(url):
    """Fetch page HTML using crawl4ai"""
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'urls': [url],
        'include_raw_html': True,
        'include_links': False,
        'include_images': False
    }
    
    try:
        response = requests.post(f"{CRAWL4AI_URL}/crawl", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success' and result.get('data'):
                return result['data'][0].get('html', '')
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def detect_per_piece_pricing(html, current_price_per_box, title):
    """Detect if product is priced per piece and extract pricing"""
    if not html:
        return None, False
    
    # Check for /each pattern in HTML
    has_per_each = bool(re.search(r'/each', html, re.IGNORECASE))
    
    # Identify per-piece product types
    per_piece_keywords = [
        'corner shelf', 'shelf', 'trim', 'edge', 'transition', 'quarter round',
        'bullnose', 'pencil', 'liner', 'chair rail', 'border', 'listello',
        'accent', 'medallion', 'insert', 'dot', 'deco', 'rope', 'crown',
        'base', 'molding', 'strip', 'piece', 'individual', 'threshold',
        'saddle', 'reducer', 'end cap', 'outside corner', 'inside corner'
    ]
    
    product_title = (title or '').lower()
    is_per_piece_product = any(keyword in product_title for keyword in per_piece_keywords)
    
    price_per_piece = None
    
    # If we have /each pattern OR it's a per-piece product type, extract pricing
    if has_per_each or is_per_piece_product:
        print(f"🔹 Detected per-piece product (has_per_each: {has_per_each}, is_per_piece_type: {is_per_piece_product})")
        
        # Extract per-piece pricing patterns
        per_piece_patterns = [
            r'\$([0-9,]+\.?\d*)/each',
            r'\$([0-9,]+\.?\d*)\s*/\s*each',
            r'([0-9,]+\.?\d*)\s*/\s*each',
            r'\$([0-9,]+\.?\d*)\s*per\s*piece',
            r'([0-9,]+\.?\d*)\s*per\s*piece',
        ]
        
        for pattern in per_piece_patterns:
            price_piece_match = re.search(pattern, html, re.IGNORECASE)
            if price_piece_match:
                price_per_piece = float(price_piece_match.group(1).replace(',', ''))
                print(f"Found price per piece in HTML: ${price_per_piece}")
                break
        
        # If we found /each but no explicit per-piece pattern, use price_per_box as price_per_piece
        if not price_per_piece and current_price_per_box and has_per_each:
            price_per_piece = float(current_price_per_box)
            print(f"Using price_per_box as price_per_piece: ${price_per_piece}")
    
    return price_per_piece, (has_per_each or is_per_piece_product)

def update_product_pricing(url, price_per_piece):
    """Update product with price_per_piece"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE product_data 
        SET price_per_piece = %s, updated_at = NOW()
        WHERE url = %s;
    """, (price_per_piece, url))
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    print("🔍 Finding products without price_per_sqft for backfill...")
    
    products = get_products_without_sqft_price()
    print(f"Found {len(products)} products without price_per_sqft")
    
    if not products:
        print("No products to backfill!")
        return
    
    updated_count = 0
    per_piece_count = 0
    
    for i, (url, sku, title, price_per_box, current_price_per_piece) in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}] Processing SKU {sku}: {title[:50]}...")
        
        # Skip if already has price_per_piece
        if current_price_per_piece:
            print(f"  ✅ Already has price_per_piece: ${current_price_per_piece}")
            continue
        
        # Fetch page HTML
        html = fetch_page_html(url)
        if not html:
            print(f"  ❌ Failed to fetch HTML")
            continue
        
        # Detect per-piece pricing
        price_per_piece, is_per_piece = detect_per_piece_pricing(html, price_per_box, title)
        
        if is_per_piece:
            per_piece_count += 1
            
            if price_per_piece:
                # Update database
                update_product_pricing(url, price_per_piece)
                updated_count += 1
                print(f"  ✅ Updated with price_per_piece: ${price_per_piece}")
            else:
                print(f"  ⚠️ Detected as per-piece but no price found")
        else:
            print(f"  ➖ Not a per-piece product")
        
        # Rate limiting
        if i < len(products):
            print(f"  ⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    print(f"\n📊 Backfill Summary:")
    print(f"  Total products processed: {len(products)}")
    print(f"  Per-piece products detected: {per_piece_count}")
    print(f"  Products updated with price_per_piece: {updated_count}")
    
    # Show results
    print(f"\n📋 To check results:")
    print("docker exec postgres psql -U postgres -c \"SELECT sku, title, price_per_box, price_per_piece FROM product_data WHERE price_per_piece IS NOT NULL ORDER BY sku;\"")

if __name__ == "__main__":
    main()