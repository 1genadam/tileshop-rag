#!/usr/bin/env python3
"""
Extract brand information examples from product pages
"""

import requests
import re
import json
import time

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def crawl_and_extract_brands(urls):
    """Crawl pages and extract brand information"""
    
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    brand_examples = {}
    
    for url in urls:
        print(f"\n{'='*60}")
        print(f"Analyzing: {url}")
        print('='*60)
        
        # Crawl page
        crawl_data = {
            "urls": [url],
            "formats": ["html"],
            "javascript": True,
            "wait_time": 15,
            "page_timeout": 60000,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
        if response.status_code != 200:
            print(f"Failed to crawl: {response.status_code}")
            continue
        
        task_id = response.json().get('task_id')
        time.sleep(20)
        
        # Get result
        for attempt in range(10):
            result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
            if result_response.status_code == 200:
                result = result_response.json()
                if result.get('status') == 'completed':
                    html_content = result.get('results', [{}])[0].get('html', '') if result.get('results') else ''
                    break
            time.sleep(2)
        else:
            print("Failed to get crawl result")
            continue
        
        if not html_content:
            print("No HTML content received")
            continue
        
        # Extract brand information
        print(f"HTML length: {len(html_content):,} characters")
        
        # 1. JSON-LD Brand extraction
        json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
        
        brands_found = {
            'json_ld_brands': [],
            'html_brands': [],
            'meta_brands': [],
            'product_title': None,
            'sku': None
        }
        
        for json_str in json_ld_matches:
            try:
                json_data = json.loads(json_str.strip())
                if json_data.get('@type') == 'Product':
                    brands_found['sku'] = json_data.get('sku')
                    brands_found['product_title'] = json_data.get('name', '')[:50] + "..."
                    
                    # Extract brand info
                    brand_info = json_data.get('brand', {})
                    if brand_info:
                        print(f"  JSON-LD Brand object: {brand_info}")
                        brands_found['json_ld_brands'].append(brand_info)
            except:
                continue
        
        # 2. HTML Brand patterns
        brand_patterns = [
            r'brand[^>]*>([^<]+)',
            r'manufacturer[^>]*>([^<]+)',
            r'"brand"[^>]*>([^<]+)',
            r'Brand:\\s*([^<\\n]+)',
            r'Manufacturer:\\s*([^<\\n]+)',
        ]
        
        for pattern in brand_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.strip() and len(match.strip()) < 100:
                    brands_found['html_brands'].append(match.strip())
        
        # 3. Meta tag brands
        meta_patterns = [
            r'<meta[^>]*name=["\']brand["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*property=["\']product:brand["\'][^>]*content=["\']([^"\']+)["\']',
        ]
        
        for pattern in meta_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            brands_found['meta_brands'].extend(matches)
        
        # 4. Look for specific brand names in embedded data
        embedded_brand_patterns = [
            r'"brand"\\s*:\\s*"([^"]+)"',
            r'"manufacturer"\\s*:\\s*"([^"]+)"',
            r'"Rush River"',  # From travertine example
            r'"The Tile Shop"',
        ]
        
        embedded_brands = []
        for pattern in embedded_brand_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            embedded_brands.extend(matches)
        
        brands_found['embedded_brands'] = list(set(embedded_brands))
        
        # Remove duplicates and clean up
        brands_found['html_brands'] = list(set(brands_found['html_brands']))
        brands_found['meta_brands'] = list(set(brands_found['meta_brands']))
        
        # Display results
        print(f"\\n📊 BRAND EXTRACTION RESULTS:")
        print(f"  SKU: {brands_found['sku']}")
        print(f"  Product: {brands_found['product_title']}")
        print(f"  JSON-LD Brands: {brands_found['json_ld_brands']}")
        print(f"  HTML Pattern Brands: {brands_found['html_brands']}")
        print(f"  Meta Tag Brands: {brands_found['meta_brands']}")
        print(f"  Embedded Brands: {brands_found['embedded_brands']}")
        
        brand_examples[url] = brands_found
    
    return brand_examples

if __name__ == "__main__":
    # Test with various product types
    test_urls = [
        "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963",
        "https://www.tileshop.com/products/claros-silver-tumbled-travertine-subway-tile-3-x-6-in-657541",
        "https://www.tileshop.com/products/marmi-imperiali-zenobia-porcelain-wall-and-floor-tile-12-in-684287",
    ]
    
    print("Extracting brand information from multiple product types...")
    brand_examples = crawl_and_extract_brands(test_urls)
    
    print(f"\\n{'='*80}")
    print("SUMMARY OF BRAND INFORMATION FOUND")
    print('='*80)
    
    for url, brands in brand_examples.items():
        print(f"\\n🔍 {url.split('/')[-1][:50]}...")
        print(f"   SKU: {brands['sku']}")
        
        # Show the most relevant brand info
        if brands['json_ld_brands']:
            for brand in brands['json_ld_brands']:
                if isinstance(brand, dict):
                    print(f"   📋 JSON-LD Brand: {brand}")
                else:
                    print(f"   📋 JSON-LD Brand: {brand}")
        
        if brands['embedded_brands']:
            print(f"   🔧 Embedded Brands: {brands['embedded_brands']}")
        
        if brands['html_brands']:
            print(f"   🌐 HTML Brands: {brands['html_brands'][:3]}...")  # First 3
    
    print(f"\\n💡 RECOMMENDATIONS:")
    print(f"1. JSON-LD brand extraction appears to be the most reliable source")
    print(f"2. 'The Tile Shop' appears to be the main retailer brand")
    print(f"3. Some products may have manufacturer brands (like 'Rush River')")
    print(f"4. Brand structure: {{@type: 'Brand', name: 'Brand Name'}}")