#!/usr/bin/env python3
"""
Download and store sitemap for offline processing
Creates a JSON file with all product URLs and timestamps
"""

import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import os

# Configuration
SITEMAP_URL = "https://www.tileshop.com/sitemap.xml"
SITEMAP_FILE = "tileshop_sitemap.json"

def download_and_parse_sitemap():
    """Download sitemap and parse into JSON format"""
    print(f"Downloading sitemap from: {SITEMAP_URL}")
    
    try:
        response = requests.get(SITEMAP_URL, timeout=30)
        response.raise_for_status()
        print(f"✓ Downloaded sitemap ({len(response.content):,} bytes)")
    except requests.RequestException as e:
        print(f"✗ Failed to download sitemap: {e}")
        return None
    
    # Parse XML
    try:
        root = ET.fromstring(response.content)
        print("✓ Parsed XML successfully")
    except ET.ParseError as e:
        print(f"✗ Failed to parse XML: {e}")
        return None
    
    # Extract URLs with metadata
    urls_data = []
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        lastmod_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
        
        if loc_elem is not None:
            url_data = {
                'url': loc_elem.text,
                'lastmod': lastmod_elem.text if lastmod_elem is not None else None,
                'scraped_at': None,  # Will be updated when scraped
                'scrape_status': 'pending'  # pending, completed, failed
            }
            urls_data.append(url_data)
    
    print(f"✓ Extracted {len(urls_data):,} URLs from sitemap")
    return urls_data

def filter_product_urls(urls_data):
    """Apply product URL filters"""
    filtered_urls = []
    
    for url_data in urls_data:
        url = url_data['url']
        # Filter conditions from n8n workflow
        if ("tileshop.com/products" in url and 
            "https://www.tileshop.com/products/,-w-," not in url and
            "https://www.tileshop.com/products/" not in url and
            "sample" not in url):
            filtered_urls.append(url_data)
    
    print(f"✓ Filtered to {len(filtered_urls):,} product URLs")
    return filtered_urls

def save_sitemap_data(urls_data):
    """Save sitemap data to JSON file"""
    sitemap_data = {
        'downloaded_at': datetime.now().isoformat(),
        'total_urls': len(urls_data),
        'status': 'ready',
        'urls': urls_data
    }
    
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(sitemap_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved sitemap data to {SITEMAP_FILE}")
    return sitemap_data

def load_sitemap_data():
    """Load existing sitemap data"""
    if not os.path.exists(SITEMAP_FILE):
        print(f"✗ Sitemap file {SITEMAP_FILE} not found")
        return None
    
    try:
        with open(SITEMAP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded sitemap data from {SITEMAP_FILE}")
        print(f"  Downloaded: {data['downloaded_at']}")
        print(f"  Total URLs: {data['total_urls']:,}")
        
        # Count status
        pending = sum(1 for url in data['urls'] if url['scrape_status'] == 'pending')
        completed = sum(1 for url in data['urls'] if url['scrape_status'] == 'completed')
        failed = sum(1 for url in data['urls'] if url['scrape_status'] == 'failed')
        
        print(f"  Status - Pending: {pending:,}, Completed: {completed:,}, Failed: {failed:,}")
        
        return data
    except (json.JSONDecodeError, KeyError) as e:
        print(f"✗ Failed to load sitemap data: {e}")
        return None

def load_categorized_sitemap_data(category):
    """Load sitemap data filtered by category"""
    CATEGORIZED_SITEMAP_FILE = "categorized_sitemap.json"
    
    if not os.path.exists(CATEGORIZED_SITEMAP_FILE):
        print(f"✗ Categorized sitemap file {CATEGORIZED_SITEMAP_FILE} not found")
        print("  Run 'python categorize_sitemap.py' first to create categorized data")
        return None
    
    try:
        with open(CATEGORIZED_SITEMAP_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get category data
        category_key = category.upper()
        if category_key not in data['categorized_products']:
            print(f"✗ Category '{category}' not found in categorized data")
            available_categories = list(data['categorized_products'].keys())
            print(f"  Available categories: {', '.join(available_categories)}")
            return None
        
        category_urls = data['categorized_products'][category_key]
        
        # Convert to standard sitemap format
        sitemap_data = {
            'downloaded_at': datetime.now().isoformat(),
            'total_urls': len(category_urls),
            'status': 'ready',
            'category': category,
            'urls': []
        }
        
        for product in category_urls:
            url_data = {
                'url': product['url'],
                'lastmod': None,
                'scraped_at': None,
                'scrape_status': 'pending'
            }
            sitemap_data['urls'].append(url_data)
        
        print(f"✓ Loaded category '{category}' sitemap data")
        print(f"  Category: {category}")
        print(f"  Total URLs: {len(category_urls):,}")
        
        return sitemap_data
    except (json.JSONDecodeError, KeyError) as e:
        print(f"✗ Failed to load categorized sitemap data: {e}")
        return None

def update_url_status(url, status, error_msg=None):
    """Update the status of a specific URL in the sitemap file"""
    data = load_sitemap_data()
    if not data:
        return False
    
    # Find and update the URL
    for url_data in data['urls']:
        if url_data['url'] == url:
            url_data['scrape_status'] = status
            url_data['scraped_at'] = datetime.now().isoformat()
            if error_msg:
                url_data['error'] = error_msg
            break
    else:
        print(f"✗ URL not found in sitemap: {url}")
        return False
    
    # Save updated data
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return True

def get_pending_urls(max_urls=None):
    """Get list of pending URLs to scrape, prioritized by scrape history"""
    data = load_sitemap_data()
    if not data:
        return []
    
    # Get all pending URLs with their metadata
    pending_url_data = [url_data for url_data in data['urls'] 
                       if url_data['scrape_status'] == 'pending']
    
    # Sort by priority:
    # 1. URLs never scraped (no scraped_at timestamp) - highest priority
    # 2. URLs with failed attempts, oldest first (by scraped_at) - retry oldest failures first
    def sort_priority(url_data):
        scraped_at = url_data.get('scraped_at')
        if scraped_at is None:
            # Never scraped - highest priority (sort key: 0, original index for stability)
            return (0, url_data.get('original_index', 0))
        else:
            # Previously attempted - sort by timestamp (oldest first)
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(scraped_at)
                return (1, timestamp)  # Lower timestamp = higher priority
            except (ValueError, TypeError):
                # Invalid timestamp - treat as never scraped
                return (0, url_data.get('original_index', 0))
    
    # Sort URLs by priority
    pending_url_data.sort(key=sort_priority)
    
    # Extract just the URLs
    pending_urls = [url_data['url'] for url_data in pending_url_data]
    
    if max_urls:
        pending_urls = pending_urls[:max_urls]
    
    return pending_urls

def get_scraping_statistics():
    """Get comprehensive scraping statistics"""
    data = load_sitemap_data()
    if not data:
        return {}
    
    from datetime import datetime
    
    stats = {
        'total_urls': len(data['urls']),
        'pending': 0,
        'completed': 0,
        'failed': 0,
        'never_attempted': 0,
        'oldest_completion': None,
        'newest_completion': None,
        'completion_rate': 0
    }
    
    completion_dates = []
    
    for url_data in data['urls']:
        status = url_data.get('scrape_status', 'pending')
        
        if status == 'pending':
            stats['pending'] += 1
            if url_data.get('scraped_at') is None:
                stats['never_attempted'] += 1
        elif status == 'completed':
            stats['completed'] += 1
            scraped_at = url_data.get('scraped_at')
            if scraped_at:
                try:
                    completion_dates.append(datetime.fromisoformat(scraped_at))
                except (ValueError, TypeError):
                    pass
        elif status == 'failed':
            stats['failed'] += 1
    
    if completion_dates:
        stats['oldest_completion'] = min(completion_dates).isoformat()
        stats['newest_completion'] = max(completion_dates).isoformat()
    
    if stats['total_urls'] > 0:
        stats['completion_rate'] = (stats['completed'] / stats['total_urls']) * 100
    
    return stats

def is_sitemap_expired(sitemap_data, max_age_days=7):
    """Check if sitemap is older than max_age_days"""
    try:
        downloaded_at = datetime.fromisoformat(sitemap_data['downloaded_at'])
        age = datetime.now() - downloaded_at
        return age.days > max_age_days
    except (KeyError, ValueError):
        return True  # If can't parse date, consider it expired

def main(force_download=False, max_age_days=7):
    """Main function to download and process sitemap with auto-refresh"""
    print("Tileshop Sitemap Downloader")
    print("=" * 50)
    
    # Check if sitemap already exists
    existing_data = load_sitemap_data()
    needs_download = force_download
    
    if existing_data and not force_download:
        is_expired = is_sitemap_expired(existing_data, max_age_days)
        downloaded_at = existing_data.get('downloaded_at', 'Unknown')
        
        if is_expired:
            print(f"\n⚠️  Sitemap is older than {max_age_days} days (downloaded: {downloaded_at})")
            print("🔄 Auto-downloading fresh sitemap...")
            needs_download = True
        else:
            print(f"\n✅ Sitemap is recent (downloaded: {downloaded_at})")
            print("✓ Using existing sitemap data")
            return existing_data
    
    if not existing_data:
        print("\n📥 No existing sitemap found")
        needs_download = True
    
    if needs_download:
        # Download and process sitemap
        print("\n🌐 Downloading fresh sitemap...")
        all_urls = download_and_parse_sitemap()
        if not all_urls:
            print("❌ Failed to download sitemap")
            if existing_data:
                print("🔄 Falling back to existing sitemap")
                return existing_data
            return None
        
        # Filter for product URLs
        product_urls = filter_product_urls(all_urls)
        
        # Save to file
        sitemap_data = save_sitemap_data(product_urls)
        
        print(f"\n✅ Sitemap ready for scraping!")
        print(f"📄 File: {SITEMAP_FILE}")
        print(f"🔗 Product URLs: {len(product_urls):,}")
        
        return sitemap_data
    
    return existing_data

if __name__ == "__main__":
    main()