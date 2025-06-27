#!/usr/bin/env python3
"""
Debug script to examine the actual HTML content and improve extraction patterns
"""

import psycopg2
import re
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def analyze_html_content():
    """Analyze the captured HTML to understand the structure"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT url, raw_html FROM product_data WHERE sku = '484963'")
            result = cursor.fetchone()
            
            if not result:
                print("No data found")
                return
                
            url, html_content = result
            print(f"Analyzing HTML for: {url}")
            print(f"HTML length: {len(html_content)} characters")
            
            # Look for price patterns
            print("\n=== PRICE ANALYSIS ===")
            price_patterns = [
                r'\$([0-9,]+\.?\d*)',
                r'([0-9,]+\.?\d*)\s*/\s*box',
                r'([0-9,]+\.?\d*)\s*/\s*sq',
                r'price[^>]*>([^<]*)',
                r'box[^>]*>([^<]*)',
                r'sq\.?\s*ft[^>]*>([^<]*)'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    print(f"Pattern '{pattern}' found: {matches[:5]}")  # Show first 5 matches
            
            # Look for structured data
            print("\n=== JSON-LD ANALYSIS ===")
            json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([^<]+)</script>', html_content, re.IGNORECASE | re.DOTALL)
            for i, json_ld in enumerate(json_ld_matches):
                try:
                    data = json.loads(json_ld)
                    print(f"JSON-LD {i+1}: {json.dumps(data, indent=2)[:500]}...")
                except:
                    print(f"JSON-LD {i+1}: Parse error")
            
            # Look for specifications content
            print("\n=== SPECIFICATIONS SEARCH ===")
            spec_keywords = ['dimensions', 'thickness', 'material', 'color', 'finish', 'application']
            for keyword in spec_keywords:
                pattern = rf'{keyword}[^>]*>([^<]*)'
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    print(f"{keyword}: {matches[:3]}")
            
            # Look for coverage and product info
            print("\n=== COVERAGE & PRODUCT INFO ===")
            coverage_patterns = [
                r'coverage[^>]*>([^<]*)',
                r'([0-9,.]+\s*sq\.?\s*ft\.?\s*per\s*box)',
                r'([0-9,.]+\s*sq\.?\s*ft\.?\s*per\s*Box)'
            ]
            
            for pattern in coverage_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    print(f"Coverage pattern '{pattern}': {matches}")
            
            # Search for specific text content around key areas
            print("\n=== TEXT CONTENT AROUND KEY AREAS ===")
            
            # Find sections with price information
            price_sections = re.findall(r'.{100}\$[0-9,]+\.?\d*.{100}', html_content, re.IGNORECASE)
            for i, section in enumerate(price_sections[:3]):
                print(f"Price section {i+1}: {section}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_html_content()