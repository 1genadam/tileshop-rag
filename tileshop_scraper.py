#!/usr/bin/env python3
"""
Tileshop Product Scraper
Scrapes product data from Tileshop pages and saves to PostgreSQL
"""

import json
import re
import requests
import psycopg2
from datetime import datetime
import time
from urllib.parse import urlparse, urljoin
import sys

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

# Sample product URLs for testing
SAMPLE_URLS = [
    "https://www.tileshop.com/products/claros-silver-tumbled-travertine-subway-tile-3-x-6-in-657541",
    "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963",
]

def get_db_connection():
    """Get PostgreSQL connection using docker exec"""
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )

def crawl_page_with_tabs(url):
    """Crawl a page and its tab variants (#description, #specifications, #resources)"""
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # URLs to crawl (main page only - specifications are embedded)
    urls_to_crawl = [
        url,
        # f"{url}#description", 
        # f"{url}#specifications",
        # f"{url}#resources"
    ]
    
    results = {}
    
    for crawl_url in urls_to_crawl:
        tab_name = crawl_url.split('#')[-1] if '#' in crawl_url else 'main'
        print(f"Crawling {tab_name}: {crawl_url}")
        
        # Submit crawl request with JavaScript execution
        crawl_data = {
            "urls": [crawl_url],
            "formats": ["html", "markdown"],
            "javascript": True,
            "wait_time": 20,  # Longer wait for JS to load tab content
            "page_timeout": 60000,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "js_code": [
                # Click on tab if it exists
                f"""
                // Wait for page to load
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                // Try to click on the specific tab - enhanced selectors
                const tabSelectors = [
                    'a[href*="#{tab_name}"]',
                    'button[data-tab="{tab_name}"]',
                    '.tab-{tab_name}',
                    '[role="tab"][aria-controls*="{tab_name}"]',
                    'a[href$="#{tab_name}"]',
                    '.tabs a[href*="{tab_name}"]',
                    '.tab-button[data-target="{tab_name}"]',
                    '.nav-tabs a[href*="{tab_name}"]'
                ];
                
                let tabFound = false;
                for (const selector of tabSelectors) {{
                    const tab = document.querySelector(selector);
                    if (tab) {{
                        console.log('Found tab with selector:', selector);
                        tab.click();
                        tabFound = true;
                        await new Promise(resolve => setTimeout(resolve, 3000));
                        break;
                    }}
                }}
                
                if (!tabFound) {{
                    console.log('No tab found for {tab_name}');
                }}
                
                // Scroll to ensure all content is loaded
                window.scrollTo(0, 0);
                await new Promise(resolve => setTimeout(resolve, 1000));
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 2000));
                window.scrollTo(0, document.body.scrollHeight / 2);
                await new Promise(resolve => setTimeout(resolve, 2000));
                """
            ] if tab_name != 'main' else []
        }
        
        response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
        
        if response.status_code != 200:
            print(f"Failed to submit crawl request for {tab_name}: {response.status_code}")
            continue
        
        task_id = response.json().get('task_id')
        print(f"Task ID for {tab_name}: {task_id}")
        
        # Wait for completion
        max_attempts = 20
        for attempt in range(max_attempts):
            result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
            
            if result_response.status_code == 200:
                result = result_response.json()
                if result.get('status') == 'completed':
                    results[tab_name] = result.get('results', [{}])[0] if result.get('results') else None
                    print(f"✓ {tab_name} completed")
                    break
                elif result.get('status') == 'failed':
                    print(f"✗ {tab_name} failed: {result}")
                    break
            
            time.sleep(2)
        
        # Small delay between requests
        time.sleep(1)
    
    return results

def extract_product_data(crawl_results, base_url):
    """Extract structured product data from crawled content"""
    main_html = crawl_results.get('main', {}).get('html', '') if crawl_results.get('main') else ''
    
    data = {
        'url': base_url,
        'sku': None,
        'title': None,
        'price_per_box': None,
        'price_per_sqft': None,
        'coverage': None,
        'finish': None,
        'color': None,
        'size_shape': None,
        'description': None,
        'specifications': {},
        'resources': None,
        'images': None,
        'collection_links': None,
        'brand': None,
        'primary_image': None,
        'image_variants': None
    }
    
    if not main_html:
        print("No main HTML content found")
        return None
    
    # Extract SKU from URL
    sku_match = re.search(r'(\d+)$', base_url)
    if sku_match:
        data['sku'] = sku_match.group(1)
    
    # Extract title from title tag or h1
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', main_html, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        title = re.sub(r'\s*-\s*The Tile Shop\s*$', '', title)
        data['title'] = title
    
    # Also try h1 tag
    if not data['title']:
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', main_html, re.IGNORECASE)
        if h1_match:
            data['title'] = h1_match.group(1).strip()
    
    # Extract JSON-LD structured data - IMPROVED
    json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', main_html, re.IGNORECASE | re.DOTALL)
    for json_ld in json_ld_matches:
        try:
            # Clean up the JSON content
            json_content = json_ld.strip()
            json_data = json.loads(json_content)
            
            print(f"Found JSON-LD: {json_data.get('@type', 'Unknown type')}")
            
            if json_data.get('@type') == 'Product':
                # Extract title
                if json_data.get('name'):
                    data['title'] = json_data['name']
                    print(f"  Title from JSON-LD: {data['title']}")
                
                # Extract SKU
                if json_data.get('sku'):
                    data['sku'] = json_data['sku']
                    print(f"  SKU from JSON-LD: {data['sku']}")
                
                # Extract description
                if json_data.get('description'):
                    # Clean HTML from description
                    desc = re.sub(r'<[^>]+>', '', json_data['description'])
                    desc = re.sub(r'\n+', ' ', desc).strip()
                    data['description'] = desc
                    print(f"  Description length: {len(desc)} chars")
                
                # Extract price from offers
                offers = json_data.get('offers', {})
                if isinstance(offers, dict) and offers.get('price'):
                    price = float(offers['price'])
                    data['price_per_box'] = price
                    print(f"  Price per box from JSON-LD: ${price}")
                
                # Extract brand information - NEW
                brand_info = json_data.get('brand', {})
                if brand_info and brand_info.get('name') and brand_info['name'].strip():
                    data['brand'] = brand_info['name']
                    print(f"  Brand from JSON-LD: {data['brand']}")
                
                # Extract primary image - NEW
                if json_data.get('image'):
                    data['primary_image'] = json_data['image']
                    print(f"  Primary image from JSON-LD: {data['primary_image']}")
                    
                    # Extract image variants from Scene7 URL
                    if 'scene7.com' in json_data['image']:
                        base_url = json_data['image'].split('?')[0]  # Remove parameters
                        image_variants = {
                            'base_url': base_url,
                            'extra_large': f"{base_url}?$ExtraLarge$",
                            'large': f"{base_url}?$Large$",
                            'medium': f"{base_url}?$Medium$",
                            'small': f"{base_url}?$Small$",
                            'thumbnail': f"{base_url}?$Thumbnail$"
                        }
                        data['image_variants'] = json.dumps(image_variants)
                        print(f"  Image variants generated: {len(image_variants)} sizes")
                
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"Error parsing JSON-LD: {e}")
            print(f"JSON content preview: {json_ld[:200]}...")
            continue
    
    # Extract price information with multiple patterns - ENHANCED
    price_patterns = [
        r'\$([0-9,]+\.?\d*)/box',
        r'\$([0-9,]+\.?\d*)\s*/\s*box',
        r'([0-9,]+\.?\d*)\s*\/\s*box',
    ]
    for pattern in price_patterns:
        price_box_match = re.search(pattern, main_html, re.IGNORECASE)
        if price_box_match:
            data['price_per_box'] = float(price_box_match.group(1).replace(',', ''))
            print(f"Found price per box in HTML: ${data['price_per_box']}")
            break
    
    # Enhanced patterns for price per sq ft
    sqft_patterns = [
        r'\$([0-9,]+\.?\d*)/Sq\.?\s*Ft\.?',
        r'\$([0-9,]+\.?\d*)\s*/\s*Sq\.?\s*Ft\.?',
        r'([0-9,]+\.?\d*)\s*/\s*Sq\.?\s*Ft\.?',
        r'\$([0-9,]+\.?\d*)\s*per\s*sq\.?\s*ft\.?',
        r'([0-9,]+\.?\d*)\s*per\s*sq\.?\s*ft\.?',
        # Look for the specific format you mentioned
        r'\$([0-9,]+\.?\d*)/Sq\. Ft\.',
    ]
    for pattern in sqft_patterns:
        price_sqft_match = re.search(pattern, main_html, re.IGNORECASE)
        if price_sqft_match:
            data['price_per_sqft'] = float(price_sqft_match.group(1).replace(',', ''))
            print(f"Found price per sq ft in HTML: ${data['price_per_sqft']}")
            break
    
    # Extract coverage - IMPROVED
    coverage_patterns = [
        r'Coverage\s+([0-9,.]+\s*sq\.?\s*ft\.?\s*per\s*Box)',
        r'([0-9,.]+\s*sq\.?\s*ft\.?\s*per\s*Box)',
        r'([0-9,.]+)\s*sq\.?\s*ft\.?\s*per\s*Box',
        r'Coverage[^>]*>([^<]*sq\.?\s*ft\.?\s*per\s*Box)',
        r'([0-9,.]+\s*sq\.?\s*ft\.?\s*coverage)',
        # Look in the content for coverage info
        r'coverage.*?([0-9,.]+\s*sq\.?\s*ft\.?)',
    ]
    for pattern in coverage_patterns:
        coverage_match = re.search(pattern, main_html, re.IGNORECASE)
        if coverage_match:
            coverage_value = coverage_match.group(1).strip()
            if coverage_value and len(coverage_value) > 3:  # Basic validation
                data['coverage'] = coverage_value
                print(f"Found coverage: {coverage_value}")
                break
    
    # Extract finish information
    finish_patterns = [
        r'Finish[^>]*>([^<]*(?:Gloss|Matte|Satin)[^<]*)',
        r'(Gloss|Matte|Satin)',
    ]
    for pattern in finish_patterns:
        finish_match = re.search(pattern, main_html, re.IGNORECASE)
        if finish_match:
            data['finish'] = finish_match.group(1).strip()
            break
    
    # Extract specifications from embedded JSON data - NEW APPROACH
    specs = {}
    
    print(f"\n--- Extracting specifications from embedded JSON data ---")
    
    # Look for the embedded product data JSON
    spec_match = re.search(r'"Specifications"\s*:\s*({.*?"PDPInfo_TechnicalDetails".*?\]\s*})', main_html, re.DOTALL)
    if spec_match:
        try:
            spec_json_str = spec_match.group(1)
            spec_data = json.loads(spec_json_str)
            
            print(f"Found embedded specifications JSON")
            
            # Extract from PDPInfo_Dimensions
            if 'PDPInfo_Dimensions' in spec_data:
                for item in spec_data['PDPInfo_Dimensions']:
                    key = item.get('Key', '').replace('PDPInfo_', '')
                    value = item.get('Value', '')
                    if key and value:
                        field_name = key.lower().replace('approximate', '').replace('size', 'dimensions')
                        specs[field_name] = value
                        print(f"  {field_name}: {value}")
                        
                        # Map to main fields
                        if 'dimensions' in field_name:
                            data['size_shape'] = value
            
            # Extract from PDPInfo_DesignInstallation  
            if 'PDPInfo_DesignInstallation' in spec_data:
                for item in spec_data['PDPInfo_DesignInstallation']:
                    key = item.get('Key', '').replace('PDPInfo_', '')
                    value = item.get('Value', '')
                    if key and value:
                        field_name = key.lower()
                        specs[field_name] = value
                        print(f"  {field_name}: {value}")
                        
                        # Map to main fields
                        if field_name == 'color':
                            data['color'] = value
                        elif field_name == 'finish':
                            data['finish'] = value
            
            # Extract from PDPInfo_TechnicalDetails
            if 'PDPInfo_TechnicalDetails' in spec_data:
                for item in spec_data['PDPInfo_TechnicalDetails']:
                    key = item.get('Key', '').replace('PDPInfo_', '')
                    value = item.get('Value', '')
                    if key and value:
                        field_name = key.lower()
                        specs[field_name] = value
                        print(f"  {field_name}: {value}")
                        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing specifications JSON: {e}")
    
    # Fallback to regex patterns if JSON extraction failed
    if not specs:
        print("JSON extraction failed, trying regex patterns...")
        
        spec_patterns = {
            'dimensions': [r'(\d+\s*x\s*\d+\s*in\.?)'],
            'material_type': [r'Material Type[^>]*>\s*([^<]+)', r'(Ceramic|Porcelain)'],
            'thickness': [r'(\d+\.?\d*\s*mm)'],
            'color': [r'Color[^>]*>\s*([^<]+)'],
            'finish': [r'(gloss|matte|satin)'],
        }
        
        for field, patterns in spec_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, main_html, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    value = re.sub(r'<[^>]+>', '', value)
                    value = re.sub(r'\s+', ' ', value).strip()
                    
                    if value and len(value) > 0 and len(value) < 100:
                        specs[field] = value
                        print(f"  {field}: {value} (regex)")
                        
                        if field == 'color':
                            data['color'] = value
                        elif field == 'dimensions':
                            data['size_shape'] = value
                        elif field == 'finish':
                            data['finish'] = value
                    break
    
    data['specifications'] = specs
    print(f"Total specifications extracted: {len(specs)}")
    
    # Calculate price per sq ft if we have both price and coverage
    if data.get('price_per_box') and data.get('coverage'):
        coverage_match = re.search(r'([0-9,.]+)', data['coverage'])
        if coverage_match:
            coverage_sqft = float(coverage_match.group(1).replace(',', ''))
            data['price_per_sqft'] = round(data['price_per_box'] / coverage_sqft, 2)
            print(f"Calculated price per sq ft: ${data['price_per_sqft']}")
    
    # Extract product images - NEW
    print(f"\n--- Extracting images ---")
    images = []
    
    # Look for images in JSON-LD and embedded data
    image_patterns = [
        r'"url":"(https://[^"]*\.scene7\.com[^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
        r'"image":"([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"',
        r'<img[^>]*src="([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"[^>]*>',
    ]
    
    for pattern in image_patterns:
        matches = re.findall(pattern, main_html, re.IGNORECASE)
        for match in matches:
            if 'signature' in match.lower() or 'oatmeal' in match.lower() or 'ceramic' in match.lower():
                if match not in images:
                    images.append(match)
                    print(f"  Found image: {match}")
    
    if images:
        data['images'] = json.dumps(images)
        print(f"Total images extracted: {len(images)}")
    
    # Extract collection links - NEW
    print(f"\n--- Extracting collection links ---")
    collection_links = []
    
    # Look for collection information in embedded JSON
    collection_patterns = [
        r'"Collection"[^}]*"href":"([^"]*)"[^}]*"text":"([^"]*)"',
        r'href="([^"]*signature[^"]*)"[^>]*>([^<]*)',
        r'"name":"([^"]*signature[^"]*)"[^}]*"url":"([^"]*)"',
    ]
    
    for pattern in collection_patterns:
        matches = re.findall(pattern, main_html, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple) and len(match) >= 2:
                link_data = {'url': match[0], 'text': match[1]}
                if link_data not in collection_links:
                    collection_links.append(link_data)
                    print(f"  Found collection link: {match[1]} -> {match[0]}")
    
    # Also look for the collection name in the product title/description
    if 'signature' in (data.get('title', '') + data.get('description', '')).lower():
        collection_links.append({
            'collection': 'Signature Collection',
            'mentioned_in': 'product_description'
        })
        print(f"  Found collection reference: Signature Collection")
    
    if collection_links:
        data['collection_links'] = json.dumps(collection_links)
        print(f"Total collection links extracted: {len(collection_links)}")
    
    # Extract description from description tab
    if crawl_results.get('description', {}).get('html'):
        desc_html = crawl_results['description']['html']
        # Try to find description content
        desc_patterns = [
            r'<div[^>]*class="[^"]*description[^"]*"[^>]*>([^<]+)',
            r'<p[^>]*>([^<]+)</p>'
        ]
        for pattern in desc_patterns:
            desc_match = re.search(pattern, desc_html, re.IGNORECASE)
            if desc_match:
                desc = re.sub(r'<[^>]+>', '', desc_match.group(1))
                if len(desc.strip()) > 50:  # Only use substantial descriptions
                    data['description'] = desc.strip()
                    break
    
    # Extract resources from resources tab
    if crawl_results.get('resources', {}).get('html'):
        res_html = crawl_results['resources']['html']
        # Look for PDF links, installation guides, etc.
        pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', res_html, re.IGNORECASE)
        if pdf_links:
            data['resources'] = json.dumps({'pdf_links': pdf_links})
    
    return data

def save_to_database(product_data, crawl_results):
    """Save product data to PostgreSQL using docker exec with temp file"""
    import subprocess
    import tempfile
    import os
    
    # Prepare the raw content - limit to reasonable size for SQL
    raw_html = crawl_results.get('main', {}).get('html', '') if crawl_results.get('main') else ''
    raw_markdown = crawl_results.get('main', {}).get('markdown', '') if crawl_results.get('main') else ''
    
    # Truncate if too large for SQL injection safety
    if len(raw_html) > 500000:  # 500KB limit for SQL
        raw_html = raw_html[:500000] + "... [TRUNCATED]"
    if len(raw_markdown) > 500000:  # 500KB limit  
        raw_markdown = raw_markdown[:500000] + "... [TRUNCATED]"
    
    # Escape single quotes for SQL
    def escape_sql(text):
        if text is None:
            return 'NULL'
        return f"'{str(text).replace(chr(39), chr(39)+chr(39))}'"
    
    # Create simplified SQL with basic data only
    insert_sql = f"""
    INSERT INTO product_data (
        url, sku, title, price_per_box, price_per_sqft, coverage,
        finish, color, size_shape, description, specifications,
        resources, images, collection_links, brand, primary_image, image_variants, scraped_at
    ) VALUES (
        {escape_sql(product_data['url'])},
        {escape_sql(product_data['sku'])},
        {escape_sql(product_data['title'])},
        {product_data['price_per_box'] or 'NULL'},
        {product_data['price_per_sqft'] or 'NULL'},
        {escape_sql(product_data['coverage'])},
        {escape_sql(product_data['finish'])},
        {escape_sql(product_data['color'])},
        {escape_sql(product_data['size_shape'])},
        {escape_sql(product_data['description'])},
        {escape_sql(json.dumps(product_data['specifications']))},
        {escape_sql(product_data['resources'])},
        {escape_sql(product_data['images'])},
        {escape_sql(product_data['collection_links'])},
        {escape_sql(product_data['brand'])},
        {escape_sql(product_data['primary_image'])},
        {escape_sql(product_data['image_variants'])},
        NOW()
    )
    ON CONFLICT (url) DO UPDATE SET
        sku = EXCLUDED.sku,
        title = EXCLUDED.title,
        price_per_box = EXCLUDED.price_per_box,
        price_per_sqft = EXCLUDED.price_per_sqft,
        coverage = EXCLUDED.coverage,
        finish = EXCLUDED.finish,
        color = EXCLUDED.color,
        size_shape = EXCLUDED.size_shape,
        description = EXCLUDED.description,
        specifications = EXCLUDED.specifications,
        resources = EXCLUDED.resources,
        images = EXCLUDED.images,
        collection_links = EXCLUDED.collection_links,
        brand = EXCLUDED.brand,
        primary_image = EXCLUDED.primary_image,
        image_variants = EXCLUDED.image_variants,
        updated_at = CURRENT_TIMESTAMP;
    """
    
    try:
        # Write SQL to temp file and execute via docker
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(insert_sql)
            temp_sql_file = f.name
        
        # Copy temp file to container and execute
        result1 = subprocess.run([
            'docker', 'cp', temp_sql_file, 'postgres:/tmp/insert.sql'
        ], capture_output=True, text=True)
        
        if result1.returncode == 0:
            result2 = subprocess.run([
                'docker', 'exec', 'postgres', 
                'psql', '-U', 'postgres', '-f', '/tmp/insert.sql'
            ], capture_output=True, text=True)
            
            if result2.returncode == 0:
                print(f"✓ Saved product data for: {product_data['url']}")
            else:
                print(f"✗ Error executing SQL: {result2.stderr}")
        else:
            print(f"✗ Error copying SQL file: {result1.stderr}")
        
        # Clean up temp file
        os.unlink(temp_sql_file)
        
    except Exception as e:
        print(f"✗ Error saving to database: {e}")

def main():
    """Main scraper function"""
    print("Starting Tileshop scraper with tab support...")
    
    for url in SAMPLE_URLS:
        print(f"\n{'='*60}")
        print(f"Processing: {url}")
        print('='*60)
        
        # Crawl the page and its tabs
        crawl_results = crawl_page_with_tabs(url)
        if not crawl_results:
            print(f"✗ Failed to crawl: {url}")
            continue
        
        # Extract product data
        product_data = extract_product_data(crawl_results, url)
        if not product_data:
            print(f"✗ Failed to extract data from: {url}")
            continue
        
        # Print extracted data
        print("\n📊 Extracted product data:")
        print("-" * 40)
        for key, value in product_data.items():
            if value and key not in ['raw_html', 'raw_markdown']:
                if key == 'specifications':
                    print(f"  {key}:")
                    for spec_key, spec_value in value.items():
                        print(f"    {spec_key}: {spec_value}")
                else:
                    print(f"  {key}: {value}")
        
        # Save to database
        print(f"\n💾 Saving to database...")
        save_to_database(product_data, crawl_results)
        
        # Wait between requests to be respectful
        print(f"\n⏳ Waiting 3 seconds before next request...")
        time.sleep(3)
    
    print(f"\n✅ Scraping completed!")
    print(f"\n📋 To check the data, run these SQL queries:")
    print("docker exec postgres psql -U postgres -c \"SELECT url, sku, title, price_per_box, price_per_sqft FROM product_data;\"")
    print("docker exec postgres psql -U postgres -c \"SELECT url, specifications FROM product_data;\"")

if __name__ == "__main__":
    main()