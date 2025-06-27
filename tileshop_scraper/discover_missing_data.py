#!/usr/bin/env python3
"""
Discover potentially missing data points from product pages
"""

import requests
import re
import json
from collections import Counter, defaultdict
import subprocess

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def crawl_page_for_analysis(url):
    """Crawl a page and return raw HTML for analysis"""
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
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
        return None
    
    task_id = response.json().get('task_id')
    
    # Wait for completion
    import time
    time.sleep(20)
    
    for attempt in range(10):
        result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
        if result_response.status_code == 200:
            result = result_response.json()
            if result.get('status') == 'completed':
                return result.get('results', [{}])[0].get('html', '') if result.get('results') else ''
            elif result.get('status') == 'failed':
                return None
        time.sleep(2)
    
    return None

def analyze_json_structures(html_content):
    """Find all JSON structures and analyze their keys"""
    print("\\n=== ANALYZING JSON STRUCTURES ===")
    
    # Find all JSON-LD scripts
    json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
    
    all_json_keys = set()
    product_json_keys = set()
    
    for i, json_str in enumerate(json_ld_matches):
        try:
            json_data = json.loads(json_str.strip())
            keys = extract_all_keys(json_data)
            all_json_keys.update(keys)
            
            if json_data.get('@type') == 'Product':
                product_json_keys.update(keys)
                print(f"Product JSON-LD {i+1} keys: {sorted(keys)}")
        except:
            continue
    
    # Find embedded JavaScript data objects
    js_object_patterns = [
        r'window\.__NEXT_DATA__\s*=\s*({.*?});',
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        r'"productData"\s*:\s*({.*?}),',
        r'"specifications"\s*:\s*({.*?})',
        r'"product"\s*:\s*({.*?})',
    ]
    
    for pattern in js_object_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        for match in matches:
            try:
                json_data = json.loads(match)
                keys = extract_all_keys(json_data)
                all_json_keys.update(keys)
                print(f"Embedded JS object keys: {sorted(keys)[:20]}...")  # Show first 20
            except:
                continue
    
    print(f"\\nTotal unique JSON keys found: {len(all_json_keys)}")
    print(f"Product-specific keys: {len(product_json_keys)}")
    
    return all_json_keys, product_json_keys

def extract_all_keys(obj, prefix=''):
    """Recursively extract all keys from a JSON object"""
    keys = set()
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            keys.update(extract_all_keys(value, full_key))
    elif isinstance(obj, list) and len(obj) > 0:
        # Analyze first item in list
        keys.update(extract_all_keys(obj[0], prefix))
    
    return keys

def analyze_html_patterns(html_content):
    """Analyze HTML patterns for potential data fields"""
    print("\\n=== ANALYZING HTML PATTERNS ===")
    
    # Look for common data patterns
    data_patterns = {
        'Prices': [
            r'\$([0-9,]+\.?\d*)',
            r'price[^>]*>([^<]+)',
            r'cost[^>]*>([^<]+)',
        ],
        'Measurements': [
            r'(\d+\s*[x×]\s*\d+\s*(?:in|inch|cm|mm))',
            r'(\d+\.?\d*\s*(?:sq\.?\s*ft|square\s*feet|sqft))',
            r'(\d+\.?\d*\s*(?:mm|cm|in|inch))',
        ],
        'Colors': [
            r'color[^>]*>([^<]+)',
            r'\b(white|black|grey|gray|brown|blue|red|green|yellow|beige|tan|cream)\b',
        ],
        'Materials': [
            r'material[^>]*>([^<]+)',
            r'\b(ceramic|porcelain|stone|marble|granite|travertine|vinyl|wood)\b',
        ],
        'Brands': [
            r'brand[^>]*>([^<]+)',
            r'manufacturer[^>]*>([^<]+)',
        ],
        'Ratings/Reviews': [
            r'rating[^>]*>([^<]+)',
            r'review[^>]*>([^<]+)',
            r'(\d+\.?\d*\s*(?:stars?|out of))',
        ],
        'Availability': [
            r'stock[^>]*>([^<]+)',
            r'availability[^>]*>([^<]+)',
            r'\b(in stock|out of stock|limited)\b',
        ],
        'Warranties': [
            r'warranty[^>]*>([^<]+)',
            r'guarantee[^>]*>([^<]+)',
            r'(\d+\s*year)',
        ]
    }
    
    pattern_results = {}
    
    for category, patterns in data_patterns.items():
        matches = set()
        for pattern in patterns:
            found = re.findall(pattern, html_content, re.IGNORECASE)
            for match in found[:10]:  # Limit to first 10 matches
                if isinstance(match, tuple):
                    match = match[0] if match else ''
                if match and len(match.strip()) > 0 and len(match.strip()) < 100:
                    matches.add(match.strip())
        
        if matches:
            pattern_results[category] = list(matches)
            print(f"{category}: {list(matches)[:5]}...")  # Show first 5
    
    return pattern_results

def analyze_data_attributes(html_content):
    """Find HTML data attributes that might contain useful info"""
    print("\\n=== ANALYZING DATA ATTRIBUTES ===")
    
    # Find all data-* attributes
    data_attrs = re.findall(r'data-([^=]+)=["\']([^"\']+)["\']', html_content)
    
    attr_summary = defaultdict(list)
    
    for attr_name, attr_value in data_attrs:
        if len(attr_value) < 200:  # Reasonable length
            attr_summary[attr_name].append(attr_value)
    
    # Show interesting data attributes
    for attr_name, values in attr_summary.items():
        if attr_name in ['price', 'sku', 'product', 'color', 'size', 'material', 'brand', 'id', 'title']:
            unique_values = list(set(values))[:5]
            print(f"data-{attr_name}: {unique_values}")
    
    return attr_summary

def analyze_meta_tags(html_content):
    """Analyze meta tags for additional product info"""
    print("\\n=== ANALYZING META TAGS ===")
    
    meta_patterns = [
        r'<meta[^>]*property=["\']([^"\']+)["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*name=["\']([^"\']+)["\'][^>]*content=["\']([^"\']+)["\']',
    ]
    
    meta_tags = {}
    
    for pattern in meta_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for prop, content in matches:
            if any(keyword in prop.lower() for keyword in ['product', 'price', 'description', 'image', 'title', 'brand']):
                meta_tags[prop] = content[:100]  # Limit length
    
    for prop, content in meta_tags.items():
        print(f"{prop}: {content}")
    
    return meta_tags

def compare_with_extracted_data():
    """Compare discovered data with what we're currently extracting"""
    print("\\n=== COMPARING WITH CURRENT EXTRACTION ===")
    
    # Get current extracted fields from database
    cmd = [
        'docker', 'exec', 'n8n-postgres', 
        'psql', '-U', 'postgres', '-c',
        "SELECT DISTINCT jsonb_object_keys(specifications) FROM product_data LIMIT 20;"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    current_fields = set()
    
    if result.returncode == 0:
        for line in result.stdout.split('\\n'):
            field = line.strip()
            if field and field != 'jsonb_object_keys' and field != '-' * 20:
                current_fields.add(field)
    
    print(f"Currently extracting {len(current_fields)} specification fields:")
    print(f"  {sorted(current_fields)}")
    
    return current_fields

def discover_missing_data(urls=None):
    """Main function to discover missing data points"""
    
    if not urls:
        # Use some test URLs
        urls = [
            "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963",
            "https://www.tileshop.com/products/claros-silver-tumbled-travertine-subway-tile-3-x-6-in-657541",
        ]
    
    print(f"Analyzing {len(urls)} product pages for missing data...")
    
    all_json_keys = set()
    all_patterns = defaultdict(set)
    all_data_attrs = defaultdict(set)
    all_meta_tags = {}
    
    for i, url in enumerate(urls, 1):
        print(f"\\n{'='*80}")
        print(f"Analyzing {i}/{len(urls)}: {url}")
        print('='*80)
        
        html_content = crawl_page_for_analysis(url)
        if not html_content:
            print("Failed to crawl page")
            continue
        
        print(f"HTML content length: {len(html_content):,} characters")
        
        # Analyze different aspects
        json_keys, product_keys = analyze_json_structures(html_content)
        pattern_results = analyze_html_patterns(html_content)
        data_attrs = analyze_data_attributes(html_content)
        meta_tags = analyze_meta_tags(html_content)
        
        # Accumulate results
        all_json_keys.update(json_keys)
        for category, patterns in pattern_results.items():
            all_patterns[category].update(patterns)
        for attr, values in data_attrs.items():
            all_data_attrs[attr].update(values)
        all_meta_tags.update(meta_tags)
    
    # Final summary
    print(f"\\n{'='*80}")
    print("SUMMARY OF POTENTIAL MISSING DATA")
    print('='*80)
    
    # Compare with current extraction
    current_fields = compare_with_extracted_data()
    
    # Show potentially interesting JSON keys we're not using
    interesting_keys = [key for key in all_json_keys if any(keyword in key.lower() 
                       for keyword in ['price', 'image', 'rating', 'review', 'warranty', 'brand', 'style', 'collection', 'series'])]
    print(f"\\nInteresting JSON keys found: {len(interesting_keys)}")
    for key in sorted(interesting_keys)[:20]:
        print(f"  {key}")
    
    # Show summary of patterns
    print(f"\\nData patterns discovered:")
    for category, patterns in all_patterns.items():
        print(f"  {category}: {len(patterns)} unique values")
    
    # Recommendations
    print(f"\\n📋 RECOMMENDATIONS:")
    print(f"1. Consider extracting image URLs (found {len([k for k in all_json_keys if 'image' in k.lower()])} image-related keys)")
    print(f"2. Look into ratings/reviews if available")
    print(f"3. Check for warranty/guarantee information")
    print(f"4. Consider brand/manufacturer details")
    print(f"5. Look for product series/collection groupings")

if __name__ == "__main__":
    discover_missing_data()