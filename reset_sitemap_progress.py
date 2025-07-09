#!/usr/bin/env python3
"""
Reset sitemap progress counters to 0
Useful when you want to start fresh learning from the beginning
"""

import json
import os

SITEMAP_FILE = "tileshop_sitemap.json"

def reset_sitemap_progress():
    """Reset all URLs in sitemap to pending status"""
    if not os.path.exists(SITEMAP_FILE):
        print(f"❌ Sitemap file {SITEMAP_FILE} not found")
        return False
    
    try:
        with open(SITEMAP_FILE, 'r') as f:
            data = json.load(f)
        
        # Reset all URLs to pending status
        reset_count = 0
        for url in data['urls']:
            if url['scrape_status'] != 'pending':
                url['scrape_status'] = 'pending'
                url['scraped_at'] = None
                reset_count += 1
        
        # Save back to file
        with open(SITEMAP_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Reset sitemap progress successfully")
        print(f"📊 Total URLs: {len(data['urls']):,}")
        print(f"🔄 Reset {reset_count:,} URLs to pending status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting sitemap progress: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Resetting Sitemap Progress...")
    print("=" * 50)
    reset_sitemap_progress()