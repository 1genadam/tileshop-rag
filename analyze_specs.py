#!/usr/bin/env python3
"""
Debug tool to analyze specifications content from actual crawl
"""

import re
import requests
import json

# Test the tab crawling to see what content we're getting
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def analyze_spec_content():
    """Analyze what's actually in the specifications tab"""
    
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    test_url = "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963#specifications"
    
    print(f"Testing: {test_url}")
    
    # Test crawl with enhanced tab navigation
    crawl_data = {
        "urls": [test_url],
        "formats": ["html"],
        "javascript": True,
        "wait_time": 25,
        "page_timeout": 60000,
        "js_code": [
            """
            // Wait for page load
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Enhanced tab clicking logic
            const allLinks = document.querySelectorAll('a');
            const allButtons = document.querySelectorAll('button');
            
            console.log('Looking for specifications tab...');
            
            // Try to find and click specifications tab
            const specSelectors = [
                'a[href*="specifications"]',
                'a[href*="#specifications"]', 
                'button[data-tab="specifications"]',
                '.tab-specifications',
                'a[href$="#specifications"]',
                '.nav-link[href*="specifications"]'
            ];
            
            let found = false;
            for (const selector of specSelectors) {
                const tabs = document.querySelectorAll(selector);
                console.log(`Selector ${selector}: found ${tabs.length} elements`);
                if (tabs.length > 0) {
                    tabs[0].click();
                    console.log(`Clicked on specifications tab with selector: ${selector}`);
                    found = true;
                    await new Promise(resolve => setTimeout(resolve, 3000));
                    break;
                }
            }
            
            if (!found) {
                console.log('No specifications tab found, checking all links...');
                for (let link of allLinks) {
                    if (link.textContent && link.textContent.toLowerCase().includes('specification')) {
                        console.log('Found specifications link:', link.textContent, link.href);
                        link.click();
                        await new Promise(resolve => setTimeout(resolve, 3000));
                        found = true;
                        break;
                    }
                }
            }
            
            // Scroll to ensure content loads
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            console.log('Final page title:', document.title);
            console.log('Page URL:', window.location.href);
            """
        ]
    }
    
    response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
    if response.status_code != 200:
        print(f"Crawl failed: {response.status_code}")
        return
    
    task_id = response.json().get('task_id')
    print(f"Task ID: {task_id}")
    
    # Wait for completion
    import time
    for attempt in range(30):
        result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
        if result_response.status_code == 200:
            result = result_response.json()
            if result.get('status') == 'completed':
                html_content = result.get('results', [{}])[0].get('html', '') if result.get('results') else ''
                print(f"Content length: {len(html_content)}")
                
                # Look for specification patterns
                spec_keywords = [
                    'approximate size', 'thickness', 'material type', 'ceramic',
                    'dimensions', 'box quantity', 'box weight', 'frost resistance',
                    'country of origin', 'applications', 'surface texture',
                    '4 x 8', 'gloss', 'subway', 'wall tile'
                ]
                
                print("\n=== SPECIFICATION CONTENT ANALYSIS ===")
                for keyword in spec_keywords:
                    pattern = rf'.{{0,100}}{re.escape(keyword)}.{{0,100}}'
                    matches = re.findall(pattern, html_content, re.IGNORECASE)
                    if matches:
                        print(f"\n{keyword.upper()}:")
                        for i, match in enumerate(matches[:2]):
                            clean_match = re.sub(r'<[^>]+>', ' ', match)
                            clean_match = re.sub(r'\s+', ' ', clean_match).strip()
                            print(f"  {i+1}: {clean_match}")
                
                # Look for structured data sections
                print("\n=== LOOKING FOR STRUCTURED SECTIONS ===")
                
                # Look for tables
                tables = re.findall(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
                print(f"Found {len(tables)} tables")
                
                # Look for definition lists
                dls = re.findall(r'<dl[^>]*>(.*?)</dl>', html_content, re.DOTALL | re.IGNORECASE)
                print(f"Found {len(dls)} definition lists")
                
                # Look for divs with spec-related classes
                spec_divs = re.findall(r'<div[^>]*class="[^"]*spec[^"]*"[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
                print(f"Found {len(spec_divs)} spec divs")
                
                if spec_divs:
                    print("Sample spec div content:")
                    sample = spec_divs[0][:500] if spec_divs else ""
                    clean_sample = re.sub(r'<[^>]+>', ' ', sample)
                    clean_sample = re.sub(r'\s+', ' ', clean_sample).strip()
                    print(f"  {clean_sample}...")
                
                break
            elif result.get('status') == 'failed':
                print(f"Task failed: {result}")
                break
        time.sleep(2)

if __name__ == "__main__":
    analyze_spec_content()