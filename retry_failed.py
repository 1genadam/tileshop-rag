#!/usr/bin/env python3
"""
Retry failed URLs from sitemap with enhanced error handling
"""

import json
import sys
from download_sitemap import load_sitemap_data, update_url_status
from acquire_from_sitemap import scrape_from_sitemap

def get_failed_urls(max_retries=None):
    """Get list of failed URLs to retry"""
    sitemap_data = load_sitemap_data()
    if not sitemap_data:
        return []
    
    failed_urls = [url_data['url'] for url_data in sitemap_data['urls'] 
                   if url_data['scrape_status'] == 'failed']
    
    if max_retries:
        failed_urls = failed_urls[:max_retries]
    
    return failed_urls

def reset_failed_to_pending(max_urls=None):
    """Reset failed URLs back to pending status for retry"""
    sitemap_data = load_sitemap_data()
    if not sitemap_data:
        print("❌ No sitemap data found")
        return 0
    
    reset_count = 0
    failed_urls = [url_data for url_data in sitemap_data['urls'] 
                   if url_data['scrape_status'] == 'failed']
    
    if max_urls:
        failed_urls = failed_urls[:max_urls]
    
    for url_data in failed_urls:
        url_data['scrape_status'] = 'pending'
        url_data['scraped_at'] = None
        # Keep error info for reference but allow retry
        if 'error' in url_data:
            url_data['previous_error'] = url_data['error']
            del url_data['error']
        reset_count += 1
    
    # Save updated sitemap
    with open('tileshop_sitemap.json', 'w', encoding='utf-8') as f:
        json.dump(sitemap_data, f, indent=2, ensure_ascii=False)
    
    return reset_count

def show_failed_summary():
    """Show summary of failed URLs and their errors"""
    sitemap_data = load_sitemap_data()
    if not sitemap_data:
        print("❌ No sitemap data found")
        return
    
    failed_urls = [url_data for url_data in sitemap_data['urls'] 
                   if url_data['scrape_status'] == 'failed']
    
    if not failed_urls:
        print("✅ No failed URLs found!")
        return
    
    print(f"📊 Failed URLs Summary ({len(failed_urls)} total):")
    print("=" * 80)
    
    # Group by error type
    error_groups = {}
    for url_data in failed_urls:
        error = url_data.get('error', 'Unknown error')
        if error not in error_groups:
            error_groups[error] = []
        error_groups[error].append(url_data['url'])
    
    for error, urls in error_groups.items():
        print(f"\n🔴 {error} ({len(urls)} URLs):")
        for i, url in enumerate(urls[:5], 1):  # Show first 5
            print(f"   {i}. {url.split('/')[-1]}")
        if len(urls) > 5:
            print(f"   ... and {len(urls) - 5} more")

def main():
    """Main retry function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            show_failed_summary()
            return
        
        elif command == 'reset':
            max_urls = None
            if len(sys.argv) > 2:
                try:
                    max_urls = int(sys.argv[2])
                except ValueError:
                    print("Invalid number for max URLs")
                    return
            
            reset_count = reset_failed_to_pending(max_urls)
            print(f"✅ Reset {reset_count} failed URLs to pending status")
            print("🔄 Run acquire_from_sitemap.py to retry them")
            return
        
        elif command == 'retry':
            max_urls = None
            if len(sys.argv) > 2:
                try:
                    max_urls = int(sys.argv[2])
                except ValueError:
                    print("Invalid number for max URLs")
                    return
            
            # Reset failed URLs to pending and run scraper
            reset_count = reset_failed_to_pending(max_urls)
            if reset_count > 0:
                print(f"🔄 Retrying {reset_count} failed URLs...")
                scrape_from_sitemap(max_urls, resume=True)
            else:
                print("✅ No failed URLs to retry")
            return
    
    # Default: show usage
    print("Tileshop Scraper - Failed URL Retry Tool")
    print("=" * 50)
    print()
    print("Usage:")
    print("  python retry_failed.py list              - Show failed URLs summary")
    print("  python retry_failed.py reset [N]         - Reset N failed URLs to pending")
    print("  python retry_failed.py retry [N]         - Reset and retry N failed URLs")
    print()
    print("Examples:")
    print("  python retry_failed.py list")
    print("  python retry_failed.py retry 10          - Retry first 10 failed URLs")
    print("  python retry_failed.py reset             - Reset all failed URLs")

if __name__ == "__main__":
    main()