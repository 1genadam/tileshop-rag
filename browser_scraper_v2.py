#!/usr/bin/env python3
"""
Real Browser Scraper v2 - Manual Save Approach
1. Opens URL in browser
2. User manually saves page as HTML (⌘+S)
3. Script reads the saved file
4. Extracts product data
"""

import os
import time
import glob
from pathlib import Path

# Import existing extraction functions
from tileshop_learner import extract_product_data, save_product_to_database

def run_applescript(script):
    """Execute AppleScript and return result"""
    import subprocess
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"AppleScript error: {result.stderr}")
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
        return "opened"
    end tell
    '''
    return run_applescript(script)

def wait_for_saved_file(downloads_dir="/Users/robertsher/Downloads", timeout=60):
    """Wait for user to save HTML file and return the newest HTML file"""
    print(f"  📁 Watching {downloads_dir} for new HTML files...")
    
    # Get existing HTML files before
    existing_files = set(glob.glob(f"{downloads_dir}/*.html"))
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_files = set(glob.glob(f"{downloads_dir}/*.html"))
        new_files = current_files - existing_files
        
        if new_files:
            # Return the newest file
            newest_file = max(new_files, key=os.path.getctime)
            print(f"  ✓ Found new file: {os.path.basename(newest_file)}")
            return newest_file
        
        time.sleep(1)
    
    print(f"  ⚠️ No new HTML file found within {timeout}s")
    return None

def scrape_product_manually(url, downloads_dir="/Users/robertsher/Downloads"):
    """Scrape product using manual save approach"""
    print(f"\n🌐 Opening in browser: {url}")
    
    # Open URL in Chrome
    if not open_url_in_chrome(url):
        print("  ❌ Failed to open URL in Chrome")
        return None
    
    print("  ⌨️  Please save the page as HTML:")
    print("     1. Wait for page to fully load")
    print("     2. Press ⌘+S (Cmd+S)")
    print("     3. Save as 'Web Page, Complete' or 'HTML Only'")
    print("     4. The script will automatically detect the saved file")
    
    # Wait for user to save file
    saved_file = wait_for_saved_file(downloads_dir, timeout=120)
    
    if not saved_file:
        print("  ❌ No file saved - skipping this product")
        return None
    
    try:
        # Read the saved HTML file
        with open(saved_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"  📄 Read {len(html_content)} characters from saved file")
        
        # Check if we got real product content
        if "High Quality Floor & Wall Tile" in html_content and "Signature Collection" in html_content:
            print("  ❌ Got homepage content - this shouldn't happen with real browser!")
            return None
        
        # Create crawl results structure for existing extraction
        crawl_results = {
            'main': {
                'html': html_content,
                'markdown': ''
            }
        }
        
        # Extract product data using existing functions
        print("  🔍 Extracting product data...")
        product_data = extract_product_data(crawl_results, url)
        
        # Clean up - delete the saved file
        os.remove(saved_file)
        print(f"  🗑️  Cleaned up saved file")
        
        return product_data
        
    except Exception as e:
        print(f"  ❌ Error reading saved file: {e}")
        return None

def scrape_products_manually(urls):
    """Scrape multiple products using manual save approach"""
    print(f"🚀 Starting manual browser scraping for {len(urls)} products")
    print("\n📋 Instructions:")
    print("   - Script will open each URL in Chrome")
    print("   - You save each page with ⌘+S")
    print("   - Script automatically processes saved files")
    print("   - Human-like timing with real interaction!")
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"\n{'='*80}")
        print(f"Processing {i+1}/{len(urls)}: {url.split('/')[-1][:50]}...")
        print(f"{'='*80}")
        
        try:
            product_data = scrape_product_manually(url)
            
            if product_data:
                # Save to database
                print(f"  💾 Saving to database...")
                save_product_to_database(product_data)
                print(f"  ✅ Successfully saved: {product_data.get('title', 'Unknown')[:50]}...")
                successful += 1
            else:
                print(f"  ❌ Failed to extract data")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {url}: {e}")
            failed += 1
        
        # Pause between products for human-like timing
        if i < len(urls) - 1:
            print(f"\n  ⏸️  Ready for next product? Press Enter to continue...")
            input()
    
    print(f"\n🎉 Manual scraping completed!")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Success rate: {successful/(successful+failed)*100:.1f}%")

# Test URLs
TEST_URLS = [
    "https://www.tileshop.com/products/penny-round-cloudy-porcelain-mosaic-wall-and-floor-tile-615826",
    "https://www.tileshop.com/products/penny-round-milk-porcelain-mosaic-wall-and-floor-tile-669029"
]

if __name__ == "__main__":
    print("🔥 Real Browser Scraper v2 - Manual Save Approach")
    print("This completely bypasses bot detection using real human interaction")
    
    # Test with a few URLs first
    scrape_products_manually(TEST_URLS)