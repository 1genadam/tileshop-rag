#!/usr/bin/env python3
"""
Scrape all products from Tileshop sitemap
Replicates the n8n workflow filter logic
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
from curl_scraper import scrape_product_with_curl, save_product_data

# Configuration
SITEMAP_URL = "https://www.tileshop.com/sitemap.xml"
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def fetch_sitemap_urls():
    """Fetch and parse sitemap.xml to get product URLs"""
    print("Fetching sitemap...")
    
    response = requests.get(SITEMAP_URL)
    if response.status_code != 200:
        print(f"Failed to fetch sitemap: {response.status_code}")
        return []
    
    # Parse XML
    root = ET.fromstring(response.content)
    
    # Extract URLs
    urls = []
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if loc_elem is not None:
            urls.append(loc_elem.text)
    
    print(f"Found {len(urls)} total URLs in sitemap")
    return urls

def filter_product_urls(urls):
    """Apply the same filter logic as the n8n workflow"""
    filtered_urls = []
    
    for url in urls:
        # Filter conditions from n8n workflow:
        # 1. Contains "tileshop.com/products"
        # 2. NOT contains "https://www.tileshop.com/products/,-w-,"
        # 3. NOT contains "sample"
        
        if ("tileshop.com/products" in url and 
            "https://www.tileshop.com/products/,-w-," not in url and
            "sample" not in url):
            filtered_urls.append(url)
    
    print(f"Filtered to {len(filtered_urls)} product URLs")
    return filtered_urls

def scrape_all_products(max_products=None):
    """Scrape all products from sitemap"""
    
    # Step 1: Fetch and filter URLs
    all_urls = fetch_sitemap_urls()
    product_urls = filter_product_urls(all_urls)
    
    if max_products:
        product_urls = product_urls[:max_products]
        print(f"Limited to first {max_products} products for testing")
    
    print(f"Starting to scrape {len(product_urls)} products...")
    
    # Statistics
    successful_scrapes = 0
    failed_scrapes = 0
    start_time = time.time()
    
    for i, url in enumerate(product_urls, 1):
        print(f"\n{'='*80}")
        print(f"Processing {i}/{len(product_urls)}: {url}")
        print('='*80)
        
        try:
            # Use curl-based enhanced extraction
            product_data = scrape_product_with_curl(url)
            
            if not product_data:
                print(f"✗ Failed to extract data from: {url}")
                failed_scrapes += 1
                continue
            
            # Print summary
            print(f"\\n📊 Extracted data for SKU {product_data.get('sku', 'unknown')}:")
            print(f"  Title: {product_data.get('title', 'N/A')[:50]}...")
            print(f"  Price: ${product_data.get('price_per_box', 'N/A')}")
            print(f"  Enhanced Specs: {len(json.loads(product_data.get('specifications', '{}'))) if product_data.get('specifications') else 0} fields")
            print(f"  Applications: {product_data.get('application_areas', 'N/A')}")
            
            # Save to database using curl scraper's save function
            if save_product_data(product_data):
                successful_scrapes += 1
            else:
                failed_scrapes += 1
            
            # Rate limiting - be respectful
            print(f"⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
            
        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
            failed_scrapes += 1
            continue
        
        # Progress update every 10 products
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(product_urls) - i) * avg_time
            print(f"\\n📈 Progress: {i}/{len(product_urls)} ({i/len(product_urls)*100:.1f}%)")
            print(f"   Successful: {successful_scrapes}, Failed: {failed_scrapes}")
            print(f"   Time elapsed: {elapsed/60:.1f}m, Estimated remaining: {remaining/60:.1f}m")
    
    # Final statistics
    elapsed = time.time() - start_time
    print(f"\\n🎉 Scraping completed!")
    print(f"   Total products processed: {len(product_urls)}")
    print(f"   Successful: {successful_scrapes}")
    print(f"   Failed: {failed_scrapes}")
    print(f"   Success rate: {successful_scrapes/len(product_urls)*100:.1f}%")
    print(f"   Total time: {elapsed/60:.1f} minutes")
    print(f"   Average time per product: {elapsed/len(product_urls):.1f} seconds")

def crawl_single_page(url):
    """Simplified crawling for single page (no tabs)"""
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print(f"Crawling: {url}")
    
    # Submit crawl request
    crawl_data = {
        "urls": [url],
        "formats": ["html", "markdown"],
        "javascript": True,
        "wait_time": 20,
        "page_timeout": 60000,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
    
    if response.status_code != 200:
        print(f"Failed to submit crawl request: {response.status_code}")
        return None
    
    task_id = response.json().get('task_id')
    print(f"Task ID: {task_id}")
    
    # Wait for completion (similar to n8n workflow)
    time.sleep(20)  # Initial wait like in n8n
    
    # Check result
    max_attempts = 10
    for attempt in range(max_attempts):
        result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
        
        if result_response.status_code == 200:
            result = result_response.json()
            if result.get('status') == 'completed':
                main_result = result.get('results', [{}])[0] if result.get('results') else None
                if main_result:
                    return {'main': main_result}
                else:
                    print("No results returned")
                    return None
            elif result.get('status') == 'failed':
                print(f"Crawl failed: {result}")
                return None
        
        time.sleep(2)
    
    print("Crawl timed out")
    return None

if __name__ == "__main__":
    import sys
    
    # Check if user wants to limit the number of products for testing
    max_products = None
    if len(sys.argv) > 1:
        try:
            max_products = int(sys.argv[1])
            print(f"Testing mode: limiting to {max_products} products")
        except ValueError:
            print("Invalid number provided, scraping all products")
    
    scrape_all_products(max_products)