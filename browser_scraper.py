#!/usr/bin/env python3
"""
Real Browser Scraper for Tileshop
Uses your actual Chrome browser to bypass bot detection
"""

import subprocess
import json
import time
import re
from datetime import datetime, timezone, timedelta

# Import existing extraction functions
from tileshop_learner import extract_product_data, get_db_connection

def run_applescript(script):
    """Execute AppleScript and return result"""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"AppleScript error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("AppleScript timeout")
        return None
    except Exception as e:
        print(f"AppleScript execution error: {e}")
        return None

def open_url_in_chrome(url):
    """Open URL in a new Chrome tab"""
    script = f'''
    tell application "Google Chrome"
        activate
        set newTab to make new tab at end of tabs of window 1
        set URL of newTab to "{url}"
        delay 5
        return "opened"
    end tell
    '''
    return run_applescript(script)

def get_page_content():
    """Get current page HTML content from Chrome"""
    script = '''
    tell application "Google Chrome"
        set pageHTML to execute active tab of window 1 javascript "document.documentElement.outerHTML"
        return pageHTML
    end tell
    '''
    return run_applescript(script)

def get_page_title():
    """Get current page title from Chrome"""
    script = '''
    tell application "Google Chrome"
        return title of active tab of window 1
    end tell
    '''
    return run_applescript(script)

def close_current_tab():
    """Close the current Chrome tab"""
    script = '''
    tell application "Google Chrome"
        close active tab of window 1
    end tell
    '''
    return run_applescript(script)

def wait_for_page_load(max_wait=30):
    """Wait for page to finish loading by checking title changes"""
    print("  ⏳ Waiting for page to load...")
    
    start_time = time.time()
    last_title = ""
    stable_count = 0
    
    while time.time() - start_time < max_wait:
        title = get_page_title()
        if title and title != "New Tab" and title != "":
            if title == last_title:
                stable_count += 1
                if stable_count >= 3:  # Title stable for 3 checks
                    print(f"  ✓ Page loaded: {title[:50]}...")
                    return True
            else:
                stable_count = 0
                last_title = title
        
        time.sleep(1)
    
    print(f"  ⚠️ Page load timeout after {max_wait}s")
    return False

def scrape_product_with_browser(url):
    """Scrape a single product using real browser"""
    print(f"\n🌐 Opening in browser: {url}")
    
    # Open URL in Chrome
    if not open_url_in_chrome(url):
        print("  ❌ Failed to open URL in Chrome")
        return None
    
    # Wait for page to load
    if not wait_for_page_load():
        print("  ❌ Page failed to load properly")
        close_current_tab()
        return None
    
    # Get page content
    print("  📄 Extracting page content...")
    html_content = get_page_content()
    
    if not html_content:
        print("  ❌ Failed to get page content")
        close_current_tab()
        return None
    
    # Check if we got homepage content (bot detection check)
    title = get_page_title()
    if "High Quality Floor & Wall Tile" in title and "Signature Collection" in html_content:
        print("  ❌ Got homepage content - unexpected!")
        close_current_tab()
        return None
    
    print(f"  ✓ Got content, title: {title[:50]}...")
    
    # Close the tab
    close_current_tab()
    
    # Create crawl results structure for existing extraction
    crawl_results = {
        'main': {
            'html': html_content,
            'markdown': ''  # We don't need markdown for this
        }
    }
    
    # Extract product data using existing functions
    product_data = extract_product_data(crawl_results, url)
    
    return product_data

def scrape_products_with_browser(urls, delay_between=10):
    """Scrape multiple products using browser automation"""
    print(f"🚀 Starting browser scraping for {len(urls)} products")
    print(f"⏱️ Using {delay_between}s delays between requests")
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"\n{'='*60}")
        print(f"Processing {i+1}/{len(urls)}: {url.split('/')[-1]}")
        print(f"{'='*60}")
        
        try:
            product_data = scrape_product_with_browser(url)
            
            if product_data:
                # Save to database using existing function
                # (You'd need to implement save_product_to_db or use existing save logic)
                print(f"  ✅ Successfully extracted: {product_data.get('title', 'Unknown')[:50]}...")
                successful += 1
            else:
                print(f"  ❌ Failed to extract data")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {url}: {e}")
            failed += 1
        
        # Human-like delay between requests
        if i < len(urls) - 1:  # Don't delay after last item
            print(f"  😴 Waiting {delay_between}s before next product...")
            time.sleep(delay_between)
    
    print(f"\n🎉 Scraping completed!")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Success rate: {successful/(successful+failed)*100:.1f}%")

# Test URLs
TEST_URLS = [
    "https://www.tileshop.com/products/penny-round-cloudy-porcelain-mosaic-wall-and-floor-tile-615826",
    "https://www.tileshop.com/products/penny-round-milk-porcelain-mosaic-wall-and-floor-tile-669029"
]

if __name__ == "__main__":
    print("🔥 Real Browser Scraper - Bypassing Bot Detection")
    print("This will use your actual Chrome browser to scrape pages")
    print("\n⚠️  Make sure Google Chrome is running")
    
    # Test with a few URLs first
    scrape_products_with_browser(TEST_URLS, delay_between=15)