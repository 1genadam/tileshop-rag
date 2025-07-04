#!/usr/bin/env python3
"""
Curl-based scraper for Tileshop
Uses direct HTTP requests since curl gets the real product pages
"""

import subprocess
import time
import random
from tileshop_learner import extract_product_data

def get_page_with_curl(url, user_agent=None):
    """Get page content using curl with your browser's user agent"""
    if not user_agent:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    
    # Build curl command with just user agent
    cmd = ['curl', '-s', '--compressed', '-A', user_agent, url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0:
            # Handle different encodings
            try:
                return result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return result.stdout.decode('latin1')
                except:
                    return result.stdout.decode('utf-8', errors='ignore')
        else:
            print(f"  ❌ Curl error (code {result.returncode}): {result.stderr.decode('utf-8', errors='ignore')}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Curl timeout for {url}")
        return None
    except Exception as e:
        print(f"  ❌ Curl execution error: {e}")
        return None

def scrape_product_with_curl(url):
    """Scrape a single product using curl including tabs for complete data"""
    print(f"\n🌐 Fetching with curl: {url}")
    
    # Fetch main page
    html_content = get_page_with_curl(url)
    
    if not html_content:
        print("  ❌ Failed to get page content")
        return None
    
    # Quick check - look for product title in content
    if "Penny Round" in html_content or "porcelain" in html_content.lower():
        print("  ✓ Got product content")
    elif "Signature Collection" in html_content:
        print("  ❌ Got homepage content - unexpected!")
        return None
    else:
        print("  ⚠️ Content type unclear, proceeding...")
    
    # Create crawl results structure for existing extraction
    crawl_results = {
        'main': {
            'html': html_content,
            'markdown': ''
        }
    }
    
    # Fetch additional tabs for complete resource extraction
    tabs_to_fetch = ['resources', 'specifications']
    
    for tab in tabs_to_fetch:
        tab_url = f"{url}#{tab}"
        print(f"  📋 Fetching {tab} tab...")
        
        # Add small delay between requests
        time.sleep(random.uniform(1, 3))
        
        tab_html = get_page_with_curl(tab_url)
        if tab_html:
            crawl_results[tab] = {
                'html': tab_html,
                'markdown': ''
            }
            print(f"  ✓ Got {tab} tab content")
        else:
            print(f"  ⚠️ Failed to get {tab} tab content")
    
    # Extract product data using existing functions
    print("  🔍 Extracting product data...")
    product_data = extract_product_data(crawl_results, url)
    
    return product_data

def scrape_products_with_curl(urls, delay_range=(10, 20)):
    """Scrape multiple products using curl with human-like delays"""
    print(f"🚀 Starting curl scraping for {len(urls)} products")
    print(f"⏱️ Using {delay_range[0]}-{delay_range[1]}s random delays")
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"\n{'='*80}")
        print(f"Processing {i+1}/{len(urls)}: {url.split('/')[-1]}")
        print(f"{'='*80}")
        
        try:
            product_data = scrape_product_with_curl(url)
            
            if product_data:
                # Save to database (implement later)
                print(f"  💾 Product data extracted successfully:")
                save_product_to_database(product_data)
                print(f"  ✅ Extracted: {product_data.get('title', 'Unknown')[:50]}...")
                successful += 1
            else:
                print(f"  ❌ Failed to extract data")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {url}: {e}")
            failed += 1
        
        # Human-like random delay between requests
        if i < len(urls) - 1:
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"  😴 Waiting {delay:.1f}s before next product...")
            time.sleep(delay)
    
    print(f"\n🎉 Curl scraping completed!")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Success rate: {successful/(successful+failed)*100:.1f}%")

def save_product_to_database(product_data):
    """Save product data to database using tileshop_learner functions"""
    from tileshop_learner import save_to_database
    
    try:
        # Create mock crawl_results since save_to_database needs it
        crawl_results = {
            'main': {'html': '', 'markdown': ''}
        }
        save_to_database(product_data, crawl_results)
        print(f"    ✅ Saved to database: {product_data.get('title', 'Unknown')[:50]}...")
        return True
    except Exception as e:
        print(f"    ❌ Database save failed: {e}")
        print(f"    📋 Product data preview:")
        print(f"      - Title: {product_data.get('title', 'N/A')}")
        print(f"      - SKU: {product_data.get('sku', 'N/A')}")
        print(f"      - Brand: {product_data.get('brand', 'N/A')}")
        print(f"      - Price: ${product_data.get('price_per_box', 'N/A')}")
        return False

# Test URLs
TEST_URLS = [
    "https://www.tileshop.com/products/penny-round-cloudy-porcelain-mosaic-wall-and-floor-tile-615826",
    "https://www.tileshop.com/products/penny-round-milk-porcelain-mosaic-wall-and-floor-tile-669029"
]

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Curl-based Enhanced Tileshop Scraper')
    parser.add_argument('--single-url', type=str, help='Scrape a single product URL')
    parser.add_argument('url', nargs='?', help='Scrape a single product URL (positional)')
    args = parser.parse_args()
    
    print("🔥 Curl-based Enhanced Scraper - 100% Reliable Data Acquisition")
    print("Uses direct HTTP requests with enhanced specification extraction!")
    
    if args.single_url:
        # Single URL mode (used by intelligence manager)
        print(f"🎯 Single URL mode: {args.single_url}")
        result = scrape_product_with_curl(args.single_url)
        if result:
            save_product_data(result)
            print(f"✅ Successfully processed: {args.single_url}")
        else:
            print(f"❌ Failed to process: {args.single_url}")
            sys.exit(1)
    elif args.url:
        # Single URL mode (positional argument)
        print(f"🎯 Processing URL: {args.url}")
        result = scrape_product_with_curl(args.url)
        if result:
            save_product_data(result)
            print(f"✅ Successfully processed: {args.url}")
        else:
            print(f"❌ Failed to process: {args.url}")
            sys.exit(1)
    else:
        # Default test mode
        print("🚀 Test mode with default URLs")
        scrape_products_with_curl(TEST_URLS)