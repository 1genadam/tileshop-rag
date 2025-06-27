#!/usr/bin/env python3
"""
Extract product image examples from different product types
"""

import requests
import re
import json
import time

# Configuration
CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_TOKEN = "tileshop"

def extract_images_from_page(url):
    """Extract all image information from a product page"""
    
    headers = {
        'Authorization': f'Bearer {CRAWL4AI_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Crawl page
    crawl_data = {
        "urls": [url],
        "formats": ["html"],
        "javascript": True,
        "wait_time": 15,
        "page_timeout": 60000,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.post(f"{CRAWL4AI_URL}/crawl", headers=headers, json=crawl_data)
    if response.status_code != 200:
        return None
    
    task_id = response.json().get('task_id')
    time.sleep(20)
    
    # Get result
    for attempt in range(10):
        result_response = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", headers=headers)
        if result_response.status_code == 200:
            result = result_response.json()
            if result.get('status') == 'completed':
                html_content = result.get('results', [{}])[0].get('html', '') if result.get('results') else ''
                break
        time.sleep(2)
    else:
        return None
    
    if not html_content:
        return None
    
    image_data = {
        'url': url,
        'sku': None,
        'title': None,
        'json_ld_images': [],
        'meta_images': [],
        'scene7_images': [],
        'product_gallery_images': [],
        'all_product_images': []
    }
    
    print(f"\n{'='*80}")
    print(f"Analyzing images for: {url}")
    print('='*80)
    
    # 1. Extract from JSON-LD
    json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
    
    for json_str in json_ld_matches:
        try:
            json_data = json.loads(json_str.strip())
            if json_data.get('@type') == 'Product':
                image_data['sku'] = json_data.get('sku')
                image_data['title'] = json_data.get('name', '')[:50] + "..."
                
                # Extract image
                if json_data.get('image'):
                    image_data['json_ld_images'].append(json_data['image'])
                    print(f"📸 JSON-LD Image: {json_data['image']}")
        except:
            continue
    
    # 2. Extract from meta tags
    meta_patterns = [
        r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
        r'<meta[^>]*property=["\']product:image["\'][^>]*content=["\']([^"\']+)["\']',
    ]
    
    for pattern in meta_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if match not in image_data['meta_images']:
                image_data['meta_images'].append(match)
                print(f"🖼️ Meta Image: {match}")
    
    # 3. Find Scene7 images (Tileshop's CDN)
    scene7_patterns = [
        r'(https://tileshop\.scene7\.com/is/image/TileShop/[^"\'\\s]+)',
        r'"url":"(https://[^"]*scene7[^"]*)"',
        r'src="(https://[^"]*scene7[^"]*)"',
    ]
    
    scene7_images = set()
    for pattern in scene7_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if 'tileshop' in match.lower() and match not in scene7_images:
                scene7_images.add(match)
    
    image_data['scene7_images'] = list(scene7_images)
    print(f"🌐 Scene7 Images found: {len(scene7_images)}")
    for img in list(scene7_images)[:5]:  # Show first 5
        print(f"   {img}")
    
    # 4. Look for product gallery/carousel images
    gallery_patterns = [
        r'"images":\s*\[([^\]]+)\]',
        r'"gallery":\s*\[([^\]]+)\]',
        r'"productImages":\s*\[([^\]]+)\]',
    ]
    
    for pattern in gallery_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        for match in matches:
            # Try to extract URLs from the JSON array
            urls = re.findall(r'"(https://[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"', match, re.IGNORECASE)
            image_data['product_gallery_images'].extend(urls)
    
    print(f"🖼️ Gallery Images found: {len(image_data['product_gallery_images'])}")
    for img in image_data['product_gallery_images'][:3]:  # Show first 3
        print(f"   {img}")
    
    # 5. Comprehensive image search
    all_image_patterns = [
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
        r'"image":\s*"([^"]+)"',
        r'"url":\s*"([^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
    ]
    
    all_images = set()
    for pattern in all_image_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            # Filter for product-related images
            if (any(term in match.lower() for term in ['tileshop', 'scene7', 'product']) and
                any(ext in match.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']) and
                len(match) > 20):  # Reasonable URL length
                all_images.add(match)
    
    image_data['all_product_images'] = list(all_images)
    print(f"🔍 All Product Images found: {len(all_images)}")
    
    return image_data

def analyze_image_patterns():
    """Analyze image patterns across different product types"""
    
    test_urls = [
        "https://www.tileshop.com/products/signature-oatmeal-frame-gloss-ceramic-subway-wall-tile-4-x-8-in-484963",
        "https://www.tileshop.com/products/claros-silver-tumbled-travertine-subway-tile-3-x-6-in-657541",
        "https://www.tileshop.com/products/marmi-imperiali-zenobia-porcelain-wall-and-floor-tile-12-in-684287",
    ]
    
    all_image_data = []
    
    for url in test_urls:
        image_data = extract_images_from_page(url)
        if image_data:
            all_image_data.append(image_data)
    
    # Summary analysis
    print(f"\n{'='*80}")
    print("IMAGE EXTRACTION SUMMARY")
    print('='*80)
    
    for data in all_image_data:
        print(f"\n🆔 SKU {data['sku']}: {data['title']}")
        print(f"   📸 JSON-LD Images: {len(data['json_ld_images'])}")
        print(f"   🖼️ Meta Images: {len(data['meta_images'])}")
        print(f"   🌐 Scene7 Images: {len(data['scene7_images'])}")
        print(f"   🎭 Gallery Images: {len(data['product_gallery_images'])}")
        print(f"   🔍 Total Product Images: {len(data['all_product_images'])}")
        
        # Show best quality images
        if data['json_ld_images']:
            print(f"   ⭐ Primary Image: {data['json_ld_images'][0]}")
        elif data['meta_images']:
            print(f"   ⭐ Primary Image: {data['meta_images'][0]}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"1. JSON-LD 'image' field is the most reliable primary image source")
    print(f"2. Meta og:image provides high-quality promotional images")
    print(f"3. Scene7 CDN images are numerous and high-quality")
    print(f"4. Image URLs follow pattern: https://tileshop.scene7.com/is/image/TileShop/[SKU]?[params]")
    print(f"5. Multiple image sizes available via Scene7 parameters (?$ExtraLarge$, ?$Large$, etc.)")
    
    return all_image_data

if __name__ == "__main__":
    print("Extracting product image examples...")
    image_data = analyze_image_patterns()
    
    print(f"\n🎯 IMPLEMENTATION RECOMMENDATIONS:")
    print(f"✅ Extract primary image from JSON-LD")
    print(f"✅ Extract meta og:image as backup")
    print(f"✅ Store Scene7 base URL for different size variants")
    print(f"✅ Consider extracting multiple gallery images for comprehensive coverage")