#!/usr/bin/env python3
"""
Category-specific parsing logic for different product types
Provides optimized parsing methods for tiles, grout, trim, and other product categories
"""

import json
import re
from typing import Dict, Any, Optional

class CategoryParser:
    """Base class for category-specific parsing logic"""
    
    def __init__(self, category: str):
        self.category = category
        
    def parse_product_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse product data with category-specific logic"""
        # Default implementation - can be overridden by subclasses
        return self._extract_common_fields(html_content, url)
    
    def _extract_common_fields(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract common fields that apply to all product types"""
        import re
        
        # Basic product information
        product_data = {
            'url': url,
            'title': self._extract_title(html_content),
            'brand': self._extract_brand(html_content),
            'images': self._extract_images(html_content),
            'description': self._extract_description(html_content),
            'category': self.category
        }
        
        return product_data
    
    def _extract_title(self, html_content: str) -> str:
        """Extract product title using regex"""
        import re
        
        # Try title tag first
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove "- The Tile Shop" suffix if present
            title = re.sub(r'\s*-\s*The Tile Shop\s*$', '', title)
            if title and title != "The Tile Shop":
                return title
        
        # Try h1 tags
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()
        
        return "Unknown Product"
    
    def _extract_brand(self, html_content: str) -> str:
        """Extract brand information using regex"""
        import re
        
        # Look for brand patterns in text
        brand_patterns = [
            r'brand["\s:]*["\s]*([A-Za-z\s]+)',
            r'manufacturer["\s:]*["\s]*([A-Za-z\s]+)',
            r'"brand":\s*"([^"]+)"'
        ]
        
        for pattern in brand_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                brand = match.group(1).strip()
                if brand and len(brand) > 2:
                    return brand
        
        return "Unknown Brand"
    
    def _extract_images(self, html_content: str) -> list:
        """Extract product images using regex"""
        import re
        
        images = []
        
        # Look for img tags with src attributes
        img_patterns = [
            r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>',
            r'<img[^>]*data-src=["\']([^"\']+)["\'][^>]*>'
        ]
        
        for pattern in img_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for src in matches:
                if src and src not in images and ('product' in src.lower() or 'tile' in src.lower()):
                    images.append(src)
        
        return images[:10]  # Limit to first 10 images
    
    def _extract_description(self, html_content: str) -> str:
        """Extract product description using regex"""
        import re
        
        # Look for description in meta tags
        desc_patterns = [
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\'][^>]*>'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                if desc and len(desc) > 10:
                    return desc
        
        return ""

class TileParser(CategoryParser):
    """Parser optimized for tile products"""
    
    def __init__(self):
        super().__init__('tiles')
    
    def parse_product_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse tile-specific product data"""
        # Get common fields
        product_data = self._extract_common_fields(html_content, url)
        
        # Add tile-specific fields
        product_data.update({
            'size_shape': self._extract_size_shape(html_content),
            'finish': self._extract_finish(html_content),
            'color': self._extract_color(html_content),
            'material': self._extract_material(html_content),
            'coverage': self._extract_coverage(html_content),
            'price_per_box': self._extract_price_per_box(html_content),
            'price_per_sqft': self._extract_price_per_sqft(html_content),
            'collection': self._extract_collection(html_content)
        })
        
        return product_data
    
    def _extract_size_shape(self, html_content: str) -> str:
        """Extract tile size and shape"""
        import re
        
        # Look for size information in various places
        size_patterns = [
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in',
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inch',
            r'(\d+\.?\d*)"?\s*x\s*(\d+\.?\d*)"?'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"{match.group(1)} x {match.group(2)} in"
        
        return "Size not specified"
    
    def _extract_finish(self, html_content: str) -> str:
        """Extract tile finish"""
        import re
        
        finish_keywords = ['polished', 'matte', 'glossy', 'textured', 'honed', 'brushed']
        
        for keyword in finish_keywords:
            if keyword in html_content.lower():
                return keyword.title()
        
        return "Finish not specified"
    
    def _extract_color(self, html_content: str) -> str:
        """Extract tile color"""
        import re
        
        # Look for color patterns in JSON-LD or product data
        color_patterns = [
            r'"color":\s*"([^"]+)"',
            r'Color["\s:]*([A-Za-z\s,]+)',
            r'color["\s:]*([A-Za-z\s,]+)'
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                color = match.group(1).strip()
                if color and len(color) > 2:
                    return color
        
        return "Color not specified"
    
    def _extract_material(self, html_content: str) -> str:
        """Extract tile material"""
        import re
        
        material_keywords = ['ceramic', 'porcelain', 'marble', 'granite', 'travertine', 'limestone', 'glass']
        
        for keyword in material_keywords:
            if keyword in html_content.lower():
                return keyword.title()
        
        return "Material not specified"
    
    def _extract_coverage(self, html_content: str) -> str:
        """Extract coverage information"""
        import re
        
        coverage_pattern = r'(\d+\.?\d*)\s*sq\.?\s*ft'
        
        match = re.search(coverage_pattern, html_content, re.IGNORECASE)
        if match:
            return f"{match.group(1)} sq ft"
        
        return "Coverage not specified"
    
    def _extract_price_per_box(self, html_content: str) -> str:
        """Extract price per box"""
        import re
        
        price_patterns = [
            r'\$(\d+\.?\d*)\s*per\s*box',
            r'\$(\d+\.?\d*)\s*/\s*box'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/box"
        
        return "Price per box not specified"
    
    def _extract_price_per_sqft(self, html_content: str) -> str:
        """Extract price per square foot"""
        import re
        
        price_patterns = [
            r'\$(\d+\.?\d*)\s*per\s*sq\.?\s*ft',
            r'\$(\d+\.?\d*)\s*/\s*sq\.?\s*ft'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/sq ft"
        
        return "Price per sq ft not specified"
    
    def _extract_collection(self, html_content: str) -> str:
        """Extract collection name"""
        import re
        
        # Look for collection patterns
        collection_patterns = [
            r'"collection":\s*"([^"]+)"',
            r'Collection["\s:]*([A-Za-z\s]+)',
            r'collection["\s:]*([A-Za-z\s]+)'
        ]
        
        for pattern in collection_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                collection = match.group(1).strip()
                if collection and len(collection) > 2:
                    return collection
        
        return "Collection not specified"

class GroutParser(CategoryParser):
    """Parser optimized for grout products"""
    
    def __init__(self):
        super().__init__('grout')
    
    def parse_product_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse grout-specific product data"""
        # Get common fields
        product_data = self._extract_common_fields(html_content, url)
        
        # Add grout-specific fields
        product_data.update({
            'grout_type': self._extract_grout_type(html_content),
            'color': self._extract_color(html_content),
            'weight': self._extract_weight(html_content),
            'coverage': self._extract_coverage(html_content),
            'price_per_unit': self._extract_price_per_unit(html_content),
            'application': self._extract_application(html_content)
        })
        
        return product_data
    
    def _extract_grout_type(self, html_content: str) -> str:
        """Extract grout type"""
        import re
        
        grout_types = ['sanded', 'unsanded', 'epoxy', 'urethane', 'acrylic']
        
        for grout_type in grout_types:
            if grout_type in html_content.lower():
                return grout_type.title()
        
        return "Grout type not specified"
    
    def _extract_color(self, html_content: str) -> str:
        """Extract grout color"""
        import re
        
        color_patterns = [
            r'"color":\s*"([^"]+)"',
            r'Color["\s:]*([A-Za-z\s,]+)',
            r'color["\s:]*([A-Za-z\s,]+)'
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                color = match.group(1).strip()
                if color and len(color) > 2:
                    return color
        
        return "Color not specified"
    
    def _extract_weight(self, html_content: str) -> str:
        """Extract weight information"""
        import re
        
        weight_patterns = [
            r'(\d+\.?\d*)\s*lbs?',
            r'(\d+\.?\d*)\s*pounds?'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"{match.group(1)} lbs"
        
        return "Weight not specified"
    
    def _extract_coverage(self, html_content: str) -> str:
        """Extract coverage information"""
        import re
        
        coverage_pattern = r'(\d+\.?\d*)\s*sq\.?\s*ft'
        
        match = re.search(coverage_pattern, html_content, re.IGNORECASE)
        if match:
            return f"{match.group(1)} sq ft"
        
        return "Coverage not specified"
    
    def _extract_price_per_unit(self, html_content: str) -> str:
        """Extract price per unit"""
        import re
        
        price_patterns = [
            r'\$(\d+\.?\d*)\s*each',
            r'\$(\d+\.?\d*)\s*/\s*each'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/each"
        
        return "Price per unit not specified"
    
    def _extract_application(self, html_content: str) -> str:
        """Extract application information"""
        applications = ['floor', 'wall', 'interior', 'exterior', 'wet area', 'dry area']
        
        found_applications = []
        
        for application in applications:
            if application in html_content.lower():
                found_applications.append(application.title())
        
        return ", ".join(found_applications) if found_applications else "Application not specified"

class TrimParser(CategoryParser):
    """Parser optimized for trim and molding products"""
    
    def __init__(self):
        super().__init__('trim_molding')
    
    def parse_product_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse trim-specific product data"""
        # Get common fields
        product_data = self._extract_common_fields(html_content, url)
        
        # Add trim-specific fields
        product_data.update({
            'trim_type': self._extract_trim_type(html_content),
            'dimensions': self._extract_dimensions(html_content),
            'color': self._extract_color(html_content),
            'material': self._extract_material(html_content),
            'length': self._extract_length(html_content),
            'price_per_piece': self._extract_price_per_piece(html_content)
        })
        
        return product_data
    
    def _extract_trim_type(self, html_content: str) -> str:
        """Extract trim type"""
        import re
        
        trim_types = ['quarter round', 'reducer', 'stair', 'bullnose', 'chair rail', 'base molding', 'skirting']
        
        for trim_type in trim_types:
            if trim_type in html_content.lower():
                return trim_type.title()
        
        return "Trim type not specified"
    
    def _extract_dimensions(self, html_content: str) -> str:
        """Extract trim dimensions"""
        import re
        
        dimension_patterns = [
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in',
            r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inch'
        ]
        
        for pattern in dimension_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"{match.group(1)} x {match.group(2)} in"
        
        return "Dimensions not specified"
    
    def _extract_color(self, html_content: str) -> str:
        """Extract trim color"""
        import re
        
        color_patterns = [
            r'"color":\s*"([^"]+)"',
            r'Color["\s:]*([A-Za-z\s,]+)',
            r'color["\s:]*([A-Za-z\s,]+)'
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                color = match.group(1).strip()
                if color and len(color) > 2:
                    return color
        
        return "Color not specified"
    
    def _extract_material(self, html_content: str) -> str:
        """Extract trim material"""
        materials = ['wood', 'metal', 'ceramic', 'porcelain', 'plastic', 'vinyl']
        
        for material in materials:
            if material in html_content.lower():
                return material.title()
        
        return "Material not specified"
    
    def _extract_length(self, html_content: str) -> str:
        """Extract trim length"""
        import re
        
        length_patterns = [
            r'(\d+\.?\d*)\s*ft',
            r'(\d+\.?\d*)\s*feet',
            r'(\d+\.?\d*)\s*inches?'
        ]
        
        for pattern in length_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                unit = 'ft' if 'ft' in match.group(0) or 'feet' in match.group(0) else 'in'
                return f"{match.group(1)} {unit}"
        
        return "Length not specified"
    
    def _extract_price_per_piece(self, html_content: str) -> str:
        """Extract price per piece"""
        import re
        
        price_patterns = [
            r'\$(\d+\.?\d*)\s*each',
            r'\$(\d+\.?\d*)\s*/\s*each',
            r'\$(\d+\.?\d*)\s*per\s*piece'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/each"
        
        return "Price per piece not specified"

def get_category_parser(category: str) -> CategoryParser:
    """Get the appropriate parser for a given category"""
    category_lower = category.lower()
    
    if category_lower in ['tiles', 'tile']:
        return TileParser()
    elif category_lower in ['grout']:
        return GroutParser()
    elif category_lower in ['trim_molding', 'trim molding', 'trim']:
        return TrimParser()
    else:
        # Default parser for other categories
        return CategoryParser(category)

def parse_product_with_category(html_content: str, url: str, category: str) -> Dict[str, Any]:
    """Parse product data using category-specific parser"""
    parser = get_category_parser(category)
    return parser.parse_product_data(html_content, url)

if __name__ == "__main__":
    # Test the parsers
    print("Category Parser System - Test Mode")
    print("=" * 50)
    
    # Test each parser
    categories = ['tiles', 'grout', 'trim_molding', 'other']
    
    for category in categories:
        parser = get_category_parser(category)
        print(f"✓ {category.title()} Parser: {parser.__class__.__name__}")
    
    print("\n✅ All parsers initialized successfully!")