#!/usr/bin/env python3
"""
Inspect tab structure on the main page
"""

import re
import requests
import json

CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def inspect_tab_structure():
    """Look at main page to understand tab structure"""
    
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    test_url = "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963"
    
    print(f"Inspecting main page: {test_url}")
    
    crawl_data = {
        "urls": [test_url],
        "formats": ["html"],
        "javascript": True,
        "wait_time": 10,
        "js_code": [
            """
            // Log all links and buttons for analysis
            const allLinks = Array.from(document.querySelectorAll('a'));
            const allButtons = Array.from(document.querySelectorAll('button'));
            
            console.log('=== ALL LINKS ===');
            allLinks.forEach((link, i) => {
                if (link.href && (link.href.includes('spec') || link.textContent.toLowerCase().includes('spec'))) {
                    console.log(`Link ${i}: ${link.textContent.trim()} -> ${link.href}`);
                    console.log(`  Classes: ${link.className}`);
                }
            });
            
            console.log('=== ALL BUTTONS ===');
            allButtons.forEach((btn, i) => {
                if (btn.textContent.toLowerCase().includes('spec') || btn.className.includes('spec')) {
                    console.log(`Button ${i}: ${btn.textContent.trim()}`);
                    console.log(`  Classes: ${btn.className}`);
                    console.log(`  Data attributes: ${Array.from(btn.attributes).map(a => a.name + '=' + a.value).join(', ')}`);
                }
            });
            
            // Look for tab containers
            const tabContainers = document.querySelectorAll('[class*="tab"], [role="tablist"], .nav-tabs');
            console.log(`Found ${tabContainers.length} tab containers`);
            
            tabContainers.forEach((container, i) => {
                console.log(`Tab container ${i}: ${container.className}`);
                const tabs = container.querySelectorAll('a, button');
                tabs.forEach(tab => {
                    console.log(`  Tab: ${tab.textContent.trim()} -> ${tab.href || 'button'}`);
                });
            });
            """
        ]
    }
    
    response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
    if response.status_code != 200:
        print(f"Crawl failed: {response.status_code}")
        return
    
    task_id = response.json().get('task_id')
    
    # Wait for completion
    import time
    for attempt in range(20):
        result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
        if result_response.status_code == 200:
            result = result_response.json()
            if result.get('status') == 'completed':
                html_content = result.get('results', [{}])[0].get('html', '') if result.get('results') else ''
                print(f"Content length: {len(html_content)}")
                
                # Look for any tab-related HTML patterns
                print("\n=== SEARCHING FOR TAB PATTERNS IN HTML ===")
                
                # Look for links with specifications
                spec_links = re.findall(r'<a[^>]*href="[^"]*spec[^"]*"[^>]*>([^<]*)</a>', html_content, re.IGNORECASE)
                print(f"Specification links: {spec_links}")
                
                # Look for hash links
                hash_links = re.findall(r'<a[^>]*href="[^"]*#[^"]*"[^>]*>([^<]*)</a>', html_content, re.IGNORECASE)
                print(f"Hash links found: {len(hash_links)}")
                for link in hash_links[:5]:
                    print(f"  {link}")
                
                # Look for tab-related classes
                tab_classes = re.findall(r'class="[^"]*tab[^"]*"', html_content, re.IGNORECASE)
                print(f"Tab-related classes: {tab_classes[:10]}")
                
                # Look for data attributes
                data_attrs = re.findall(r'data-[^=]*="[^"]*"', html_content)
                tab_data = [attr for attr in data_attrs if 'tab' in attr.lower() or 'spec' in attr.lower()]
                print(f"Tab/spec data attributes: {tab_data[:10]}")
                
                # Look for the word "specifications" in the HTML
                spec_contexts = re.findall(r'.{0,50}specifications?.{0,50}', html_content, re.IGNORECASE)
                print(f"\nContexts with 'specifications': {len(spec_contexts)}")
                for i, context in enumerate(spec_contexts[:5]):
                    clean_context = re.sub(r'<[^>]+>', ' ', context)
                    clean_context = re.sub(r'\s+', ' ', clean_context).strip()
                    print(f"  {i+1}: {clean_context}")
                
                break
            elif result.get('status') == 'failed':
                print(f"Task failed: {result}")
                break
        time.sleep(2)

if __name__ == "__main__":
    inspect_tab_structure()