#!/usr/bin/env python3
"""
Sitemap Product Categorization System
Analyzes tileshop sitemap and categorizes products by type for selective learning.
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple
import urllib.parse

class ProductCategorizer:
    def __init__(self):
        self.categories = {
            'TILES': {
                'patterns': [
                    r'.*-tile-.*',
                    r'.*porcelain.*',
                    r'.*ceramic.*',
                    r'.*marble.*',
                    r'.*travertine.*',
                    r'.*limestone.*',
                    r'.*granite.*',
                    r'.*slate.*',
                    r'.*quartzite.*',
                    r'.*glass.*tile.*',
                    r'.*mosaic.*',
                    r'.*subway.*',
                    r'.*penny.*round.*',
                    r'.*hexagon.*tile.*'
                ],
                'keywords': ['tile', 'porcelain', 'ceramic', 'marble', 'travertine', 'mosaic'],
                'description': 'Floor and wall tiles (ceramic, porcelain, natural stone)'
            },
            'GROUT': {
                'patterns': [
                    r'.*grout.*',
                    r'.*sanded.*grout.*',
                    r'.*unsanded.*grout.*',
                    r'.*epoxy.*grout.*'
                ],
                'keywords': ['grout'],
                'description': 'Grout products (sanded, unsanded, epoxy)'
            },
            'TRIM_MOLDING': {
                'patterns': [
                    r'.*quarter.*round.*',
                    r'.*flush.*stair.*',
                    r'.*overlap.*stair.*',
                    r'.*reducer.*',
                    r'.*t.*molding.*',
                    r'.*skirting.*',
                    r'.*trim.*',
                    r'.*bullnose.*',
                    r'.*chair.*rail.*',
                    r'.*base.*molding.*',
                    r'.*corner.*trim.*'
                ],
                'keywords': ['trim', 'molding', 'quarter-round', 'reducer', 'stair', 'skirting'],
                'description': 'Trim and molding pieces (reducers, quarter rounds, stairs)'
            },
            'TOOLS_ACCESSORIES': {
                'patterns': [
                    r'.*tool.*',
                    r'.*spacer.*',
                    r'.*trowel.*',
                    r'.*float.*',
                    r'.*bucket.*',
                    r'.*mixing.*',
                    r'.*measuring.*',
                    r'.*installation.*kit.*',
                    r'.*adhesive.*',
                    r'.*primer.*',
                    r'.*sealer.*',
                    r'.*cleaner.*'
                ],
                'keywords': ['tool', 'spacer', 'trowel', 'bucket', 'kit', 'adhesive', 'sealer'],
                'description': 'Installation tools and accessories'
            },
            'NATURAL_STONE': {
                'patterns': [
                    r'.*natural.*stone.*',
                    r'.*stone.*tile.*',
                    r'.*fieldstone.*',
                    r'.*river.*rock.*',
                    r'.*pebble.*',
                    r'.*cobble.*'
                ],
                'keywords': ['stone', 'fieldstone', 'river', 'pebble', 'cobble'],
                'description': 'Natural stone products'
            },
            'METAL_GLASS': {
                'patterns': [
                    r'.*metal.*',
                    r'.*steel.*',
                    r'.*aluminum.*',
                    r'.*copper.*',
                    r'.*glass.*',
                    r'.*mirror.*'
                ],
                'keywords': ['metal', 'steel', 'aluminum', 'glass', 'mirror'],
                'description': 'Metal and glass tiles'
            },
            'DECORATIVE': {
                'patterns': [
                    r'.*accent.*',
                    r'.*border.*',
                    r'.*listello.*',
                    r'.*medallion.*',
                    r'.*insert.*',
                    r'.*feature.*'
                ],
                'keywords': ['accent', 'border', 'listello', 'medallion', 'feature'],
                'description': 'Decorative and accent pieces'
            },
            'UNCATEGORIZED': {
                'patterns': [],
                'keywords': [],
                'description': 'Products that do not match other categories'
            }
        }
    
    def categorize_url(self, url: str) -> str:
        """Categorize a single product URL"""
        # Extract product name from URL
        product_name = url.split('/')[-1].lower()
        
        # Remove SKU numbers from end for better pattern matching
        product_name = re.sub(r'-\d+$', '', product_name)
        
        for category, config in self.categories.items():
            if category == 'UNCATEGORIZED':
                continue
                
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, product_name, re.IGNORECASE):
                    return category
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in product_name:
                    return category
        
        return 'UNCATEGORIZED'
    
    def analyze_sitemap(self, sitemap_file: str) -> Dict:
        """Analyze entire sitemap and categorize all products"""
        print(f"Loading sitemap from {sitemap_file}...")
        
        with open(sitemap_file, 'r') as f:
            sitemap_data = json.load(f)
        
        categorized = defaultdict(list)
        category_counts = defaultdict(int)
        
        total_urls = len(sitemap_data.get('urls', []))
        print(f"Analyzing {total_urls:,} URLs...")
        
        for i, url_data in enumerate(sitemap_data.get('urls', [])):
            url = url_data.get('url', '')
            category = self.categorize_url(url)
            
            categorized[category].append({
                'url': url,
                'sku': self.extract_sku_from_url(url),
                'product_name': self.extract_product_name(url),
                'scrape_status': url_data.get('scrape_status', 'pending')
            })
            category_counts[category] += 1
            
            # Progress indicator
            if (i + 1) % 500 == 0 or i == total_urls - 1:
                print(f"  Processed {i+1:,}/{total_urls:,} URLs...")
        
        return {
            'categorized_products': dict(categorized),
            'category_counts': dict(category_counts),
            'total_products': total_urls,
            'analysis_summary': self.generate_summary(category_counts)
        }
    
    def extract_sku_from_url(self, url: str) -> str:
        """Extract SKU from URL (last number)"""
        match = re.search(r'-(\d+)$', url)
        return match.group(1) if match else ''
    
    def extract_product_name(self, url: str) -> str:
        """Extract readable product name from URL"""
        product_slug = url.split('/')[-1]
        # Remove SKU and convert to readable format
        name = re.sub(r'-\d+$', '', product_slug)
        name = name.replace('-', ' ').title()
        return name
    
    def generate_summary(self, category_counts: Dict[str, int]) -> str:
        """Generate analysis summary"""
        total = sum(category_counts.values())
        summary = [
            "=== SITEMAP CATEGORIZATION SUMMARY ===",
            f"Total Products: {total:,}",
            ""
        ]
        
        # Sort categories by count (descending)
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            percentage = (count / total * 100) if total > 0 else 0
            description = self.categories.get(category, {}).get('description', '')
            summary.append(f"{category:.<20} {count:>6,} ({percentage:5.1f}%) - {description}")
        
        return "\n".join(summary)
    
    def save_categorized_sitemap(self, analysis: Dict, output_file: str):
        """Save categorized sitemap to file"""
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"\nCategorized sitemap saved to: {output_file}")
    
    def generate_category_selection_data(self, analysis: Dict) -> Dict:
        """Generate data for dashboard category selection dropdown"""
        categories = []
        
        for category, count in analysis['category_counts'].items():
            if count > 0:  # Only include categories with products
                categories.append({
                    'id': category.lower(),
                    'name': category.replace('_', ' ').title(),
                    'description': self.categories.get(category, {}).get('description', ''),
                    'count': count,
                    'percentage': round((count / analysis['total_products']) * 100, 1)
                })
        
        # Sort by count (largest first)
        categories.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'categories': categories,
            'total_products': analysis['total_products'],
            'generated_at': '2025-07-03T12:00:00Z'
        }

def main():
    """Main function to categorize sitemap"""
    categorizer = ProductCategorizer()
    
    # Analyze current sitemap
    analysis = categorizer.analyze_sitemap('tileshop_sitemap.json')
    
    # Print summary
    print("\n" + analysis['analysis_summary'])
    
    # Save full categorized data
    categorizer.save_categorized_sitemap(analysis, 'categorized_sitemap.json')
    
    # Generate dashboard selection data
    selection_data = categorizer.generate_category_selection_data(analysis)
    
    with open('category_selection.json', 'w') as f:
        json.dump(selection_data, f, indent=2)
    
    print(f"\nCategory selection data saved to: category_selection.json")
    
    # Show category breakdown for dashboard
    print("\n=== DASHBOARD CATEGORY OPTIONS ===")
    for cat in selection_data['categories']:
        print(f"📁 {cat['name']}: {cat['count']:,} products ({cat['percentage']}%)")
        print(f"   {cat['description']}")

if __name__ == "__main__":
    main()