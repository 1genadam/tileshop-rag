#!/usr/bin/env python3
"""
Specialized Product Page Parsers for Tileshop
High-precision parsers optimized for specific product page structures
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from page_structure_detector import PageType, PageStructure

class BaseProductParser(ABC):
    """Base class for all specialized product parsers"""
    
    def __init__(self, page_type: PageType):
        self.page_type = page_type
        self.extraction_patterns = self._build_extraction_patterns()
    
    @abstractmethod
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        """Build extraction patterns specific to this parser"""
        pass
    
    @abstractmethod
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse product data using specialized logic for this page type"""
        pass
    
    def _extract_json_ld_data(self, html_content: str) -> Dict[str, Any]:
        """Extract and parse JSON-LD structured data"""
        json_ld_matches = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', 
            html_content, 
            re.IGNORECASE | re.DOTALL
        )
        
        for json_ld in json_ld_matches:
            try:
                json_data = json.loads(json_ld.strip())
                if json_data.get('@type') == 'Product':
                    return json_data
            except json.JSONDecodeError:
                continue
        
        return {}
    
    def _extract_sku_from_url(self, url: str) -> Optional[str]:
        """Extract SKU from URL using consistent 6-digit pattern"""
        sku_match = re.search(r'(\d{6})$', url)
        return sku_match.group(1) if sku_match else None
    
    def _clean_html_text(self, text: str) -> str:
        """Clean HTML entities and extra whitespace from text"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

class TilePageParser(BaseProductParser):
    """Specialized parser for tile product pages"""
    
    def __init__(self):
        super().__init__(PageType.TILE)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "size_patterns": [
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in\.?',
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inch',
                r'(\d+\.?\d*)"?\s*x\s*(\d+\.?\d*)"?'
            ],
            "coverage_patterns": [
                r'(\d+\.?\d*)\s*sq\.?\s*ft\.?\s*per\s*box',
                r'(\d+\.?\d*)\s*sqft\s*per\s*box',
                r'coverage[:\s]*(\d+\.?\d*)\s*sq\.?\s*ft'
            ],
            "material_keywords": ["marble", "ceramic", "porcelain", "travertine", "granite", "limestone", "glass"],
            "finish_keywords": ["polished", "honed", "matte", "glossy", "textured", "brushed", "natural"],
            "price_patterns": [
                r'\$(\d+\.?\d*)\s*per\s*box',
                r'\$(\d+\.?\d*)\s*/\s*box',
                r'price[:\s]*\$(\d+\.?\d*)'
            ]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse tile-specific product data with high precision - JSON-LD priority"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize product data with JSON-LD as primary source
        product_data = self._extract_from_json_ld_primary(json_ld_data, url)
        
        # Enhance with tile-specific extraction from HTML
        html_data = self._extract_tile_specific_data(html_content, url)
        
        # Merge data, prioritizing JSON-LD for essential fields
        for key, value in html_data.items():
            if key not in product_data or not product_data[key]:
                product_data[key] = value
        
        # Apply per-piece pricing logic for products like mortar, adhesive, etc.
        self._apply_per_piece_pricing_logic(product_data, html_content)
        
        return product_data
    
    def _extract_from_json_ld_primary(self, json_ld_data: Dict, url: str) -> Dict[str, Any]:
        """Extract primary product data from JSON-LD structured data"""
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_box': None,
            'price_per_sqft': None,
            'price_per_piece': None,
            'coverage': None,
            'size_shape': None,
            'material': None,
            'finish': None,
            'color': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'TilePageParser'
        }
        
        # Extract from JSON-LD first (most reliable)
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_box'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
            
            # Extract description
            if json_ld_data.get('description'):
                product_data['description'] = self._clean_html_text(json_ld_data['description'])
            
            # Extract SKU if not found in URL
            if json_ld_data.get('sku') and not product_data['sku']:
                product_data['sku'] = json_ld_data['sku']
        
        return product_data
    
    def _extract_tile_specific_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract tile-specific data from HTML content"""
        tile_data = {
            'size_shape': None,
            'coverage': None,
            'material': None,
            'finish': None,
            'color': None
        }
        
        content_lower = html_content.lower()
        
        # Extract size/shape
        for pattern in self.extraction_patterns["size_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                tile_data['size_shape'] = f"{match.group(1)} x {match.group(2)} in."
                break
        
        # Extract coverage
        for pattern in self.extraction_patterns["coverage_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                tile_data['coverage'] = f"{match.group(1)} sq ft"
                break
        
        # Extract material
        for material in self.extraction_patterns["material_keywords"]:
            if material in content_lower:
                tile_data['material'] = material.title()
                break
        
        # Extract finish
        for finish in self.extraction_patterns["finish_keywords"]:
            if finish in content_lower:
                tile_data['finish'] = finish.title()
                break
        
        return tile_data
    
    def _apply_per_piece_pricing_logic(self, product_data: Dict[str, Any], html_content: str) -> None:
        """Apply per-piece pricing logic for products like mortar, adhesive, grout, etc."""
        # Detect if this is a per-piece product type
        per_piece_keywords = [
            'corner shelf', 'shelf', 'trim', 'edge', 'transition', 'quarter round',
            'bullnose', 'pencil', 'liner', 'chair rail', 'border', 'listello',
            'accent', 'medallion', 'insert', 'dot', 'deco', 'rope', 'crown',
            'base', 'molding', 'strip', 'piece', 'individual', 'mortar', 'adhesive',
            'grout', 'sealer', 'cleaner', 'bag', 'bottle', 'tube', 'container'
        ]
        
        product_title = (product_data.get('title') or '').lower()
        is_per_piece_product = any(keyword in product_title for keyword in per_piece_keywords)
        
        # Detect per-unit pricing patterns in HTML content
        per_unit_patterns = [
            r'/each\b', r'per\s*each\b', r'/bag\b', r'per\s*bag\b', r'/bottle\b', r'per\s*bottle\b',
            r'/tube\b', r'per\s*tube\b', r'/container\b', r'per\s*container\b', r'/piece\b', r'per\s*piece\b'
        ]
        
        has_per_unit = any(re.search(pattern, html_content, re.IGNORECASE) for pattern in per_unit_patterns)
        
        # If we have per-unit pattern OR it's a per-piece product type, handle pricing accordingly
        if has_per_unit or is_per_piece_product:
            print(f"🔹 TilePageParser: Detected per-piece product (has_per_unit: {has_per_unit}, is_per_piece_type: {is_per_piece_product})")
            
            # Extract per-piece pricing patterns
            per_piece_patterns = [
                r'\$([0-9,]+\.?\d*)/each\b',
                r'\$([0-9,]+\.?\d*)\s*/\s*each\b',
                r'\$([0-9,]+\.?\d*)\s*per\s*piece\b',
                r'\$([0-9,]+\.?\d*)/bag\b',
                r'\$([0-9,]+\.?\d*)\s*/\s*bag\b',
                r'\$([0-9,]+\.?\d*)\s*per\s*bag\b',
                r'\$([0-9,]+\.?\d*)/bottle\b',
                r'\$([0-9,]+\.?\d*)\s*/\s*bottle\b',
                r'\$([0-9,]+\.?\d*)\s*per\s*bottle\b',
                r'\$([0-9,]+\.?\d*)/tube\b',
                r'\$([0-9,]+\.?\d*)\s*/\s*tube\b',
                r'\$([0-9,]+\.?\d*)\s*per\s*tube\b',
            ]
            
            for pattern in per_piece_patterns:
                price_piece_match = re.search(pattern, html_content, re.IGNORECASE)
                if price_piece_match:
                    product_data['price_per_piece'] = float(price_piece_match.group(1).replace(',', ''))
                    print(f"TilePageParser: Found price per piece in HTML: ${product_data['price_per_piece']}")
                    break
            
            # If we found per-unit pattern but no explicit per-piece price, use price_per_box as price_per_piece
            # BUT only if this is truly a per-piece product (not a standard tile with box+sqft pricing)
            if not product_data.get('price_per_piece') and product_data.get('price_per_box') and has_per_unit:
                # Check if this is a standard tile product (has both box and sqft pricing)
                if product_data.get('price_per_sqft'):
                    # This is a standard tile product sold by box - leave price_per_piece as None
                    print(f"TilePageParser: Standard tile product detected with box+sqft pricing - price_per_piece remains None")
                else:
                    # This is truly a per-piece product
                    product_data['price_per_piece'] = product_data['price_per_box']
                    product_data['price_per_box'] = None  # Clear box price since this is per-piece pricing
                    print(f"TilePageParser: Per-piece product detected: price_per_piece=${product_data['price_per_piece']}, cleared price_per_box")

class GroutPageParser(BaseProductParser):
    """Specialized parser for grout product pages"""
    
    def __init__(self):
        super().__init__(PageType.GROUT)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "weight_patterns": [
                r'(\d+)\s*lb\.?(?:\s|$)',
                r'(\d+)\s*lbs\.?(?:\s|$)',
                r'(\d+)\s*pounds?'
            ],
            "grout_types": ["sanded", "unsanded", "epoxy", "urethane", "acrylic"],
            "color_patterns": [
                r'color[:\s]*([a-zA-Z\s]+)',
                r'colour[:\s]*([a-zA-Z\s]+)'
            ],
            "brand_keywords": ["mapei", "custom", "superior", "laticrete", "bostik"]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse grout-specific product data with high precision"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize product data
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_piece': None,  # Grout is typically per package
            'weight': None,
            'grout_type': None,
            'color': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'GroutPageParser'
        }
        
        # Extract from JSON-LD
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price (grout is per package)
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_piece'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
        
        # Extract grout-specific information
        content_lower = html_content.lower()
        
        # Extract weight
        for pattern in self.extraction_patterns["weight_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['weight'] = f"{match.group(1)} lbs"
                break
        
        # Extract grout type
        for grout_type in self.extraction_patterns["grout_types"]:
            if grout_type in content_lower:
                product_data['grout_type'] = grout_type.title()
                break
        
        # Extract color
        for pattern in self.extraction_patterns["color_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                color = match.group(1).strip()
                if len(color) > 2 and len(color) < 20:  # Reasonable color name length
                    product_data['color'] = color.title()
                    break
        
        # Build specifications
        specs = {}
        if product_data['weight']:
            specs['weight'] = product_data['weight']
        if product_data['grout_type']:
            specs['grout_type'] = product_data['grout_type']
        if product_data['color']:
            specs['color'] = product_data['color']
        
        product_data['specifications'] = specs
        
        return product_data

class TrimMoldingPageParser(BaseProductParser):
    """Specialized parser for trim and molding product pages"""
    
    def __init__(self):
        super().__init__(PageType.TRIM_MOLDING)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "dimension_patterns": [
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*in\.?',
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*inch'
            ],
            "trim_types": ["t-molding", "quarter round", "reducer", "stair nose", "threshold", "bullnose", "cove"],
            "piece_patterns": [
                r'(\d+)\s*pieces?\s*per\s*box',
                r'box\s*contains\s*(\d+)\s*pieces?',
                r'(\d+)\s*pcs?\s*per\s*box'
            ],
            "linear_patterns": [
                r'(\d+\.?\d*)\s*ft\.?\s*per\s*piece',
                r'(\d+\.?\d*)\s*feet\s*per\s*piece',
                r'(\d+\.?\d*)\s*linear\s*feet'
            ]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse trim/molding-specific product data with high precision"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize product data
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_box': None,
            'price_per_piece': None,
            'dimensions': None,
            'trim_type': None,
            'pieces_per_box': None,
            'linear_feet': None,
            'material': None,
            'color': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'TrimMoldingPageParser'
        }
        
        # Extract from JSON-LD
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_box'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
        
        # Extract trim-specific information
        content_lower = html_content.lower()
        
        # Extract dimensions
        for pattern in self.extraction_patterns["dimension_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['dimensions'] = f"{match.group(1)} x {match.group(2)} in."
                break
        
        # Extract trim type
        for trim_type in self.extraction_patterns["trim_types"]:
            if trim_type in content_lower:
                product_data['trim_type'] = trim_type.title()
                break
        
        # Extract pieces per box
        for pattern in self.extraction_patterns["piece_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['pieces_per_box'] = int(match.group(1))
                # Calculate price per piece if we have both values
                if product_data['price_per_box'] and product_data['pieces_per_box']:
                    product_data['price_per_piece'] = round(
                        product_data['price_per_box'] / product_data['pieces_per_box'], 2
                    )
                break
        
        # Extract linear feet information
        for pattern in self.extraction_patterns["linear_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['linear_feet'] = f"{match.group(1)} ft per piece"
                break
        
        # Build specifications
        specs = {}
        if product_data['dimensions']:
            specs['dimensions'] = product_data['dimensions']
        if product_data['trim_type']:
            specs['trim_type'] = product_data['trim_type']
        if product_data['pieces_per_box']:
            specs['pieces_per_box'] = str(product_data['pieces_per_box'])
        if product_data['linear_feet']:
            specs['linear_feet'] = product_data['linear_feet']
        
        product_data['specifications'] = specs
        
        return product_data

class LuxuryVinylPageParser(BaseProductParser):
    """Specialized parser for luxury vinyl product pages"""
    
    def __init__(self):
        super().__init__(PageType.LUXURY_VINYL)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "wear_layer_patterns": [
                r'(\d+)\s*mil\s*wear\s*layer',
                r'wear\s*layer[:\s]*(\d+)\s*mil',
                r'(\d+)\s*mil'
            ],
            "thickness_patterns": [
                r'(\d+\.?\d*)\s*mm\s*thick',
                r'thickness[:\s]*(\d+\.?\d*)\s*mm',
                r'(\d+\.?\d*)\s*mm'
            ],
            "installation_keywords": ["click-and-lock", "floating", "glue-down", "loose lay"],
            "coverage_patterns": [
                r'(\d+\.?\d*)\s*sq\.?\s*ft\.?\s*per\s*box',
                r'coverage[:\s]*(\d+\.?\d*)\s*sq\.?\s*ft'
            ]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse luxury vinyl-specific product data with high precision"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize product data
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_box': None,
            'price_per_sqft': None,
            'coverage': None,
            'size_shape': None,
            'wear_layer': None,
            'thickness': None,
            'installation_method': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'LuxuryVinylPageParser'
        }
        
        # Extract from JSON-LD
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_box'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
        
        # Extract luxury vinyl-specific information
        content_lower = html_content.lower()
        
        # Extract wear layer
        for pattern in self.extraction_patterns["wear_layer_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['wear_layer'] = f"{match.group(1)} MIL"
                break
        
        # Extract thickness
        for pattern in self.extraction_patterns["thickness_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['thickness'] = f"{match.group(1)}mm"
                break
        
        # Extract installation method
        for method in self.extraction_patterns["installation_keywords"]:
            if method in content_lower:
                product_data['installation_method'] = method.title()
                break
        
        # Extract coverage and calculate price per sqft
        for pattern in self.extraction_patterns["coverage_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                product_data['coverage'] = f"{match.group(1)} sq. ft. per Box"
                if product_data['price_per_box'] and match.group(1):
                    try:
                        coverage_value = float(match.group(1))
                        product_data['price_per_sqft'] = round(
                            product_data['price_per_box'] / coverage_value, 2
                        )
                    except (ValueError, ZeroDivisionError):
                        pass
                break
        
        # Build specifications
        specs = {}
        if product_data['wear_layer']:
            specs['wear_layer'] = product_data['wear_layer']
        if product_data['thickness']:
            specs['thickness'] = product_data['thickness']
        if product_data['installation_method']:
            specs['installation_method'] = product_data['installation_method']
        if product_data['coverage']:
            specs['coverage'] = product_data['coverage']
        
        product_data['specifications'] = specs
        
        return product_data

class InstallationToolPageParser(BaseProductParser):
    """Specialized parser for installation tool pages (leveling systems, wedges, etc.)"""
    
    def __init__(self):
        super().__init__(PageType.INSTALLATION_TOOL)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "quantity_patterns": [
                r'(\d+)\s*(?:pieces?|pcs?|ea\.?)\s*per\s*(?:bag|box|pack)',
                r'(\d+)\s*(?:pieces?|pcs?|ea\.?)',
                r'(\d+)\s*count'
            ],
            "weight_patterns": [
                r'(\d+\.?\d*)\s*lbs?\.',
                r'(\d+\.?\d*)\s*pounds?',
                r'weight[:\s]*(\d+\.?\d*)\s*lbs?'
            ],
            "tool_keywords": ["leveling", "wedge", "spacer", "trowel", "float", "grout", "installation"],
            "brand_keywords": ["best of everything", "raimondi", "marshalltown", "qep", "perfect level master"]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Parse installation tool product data with JSON-LD priority"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize product data with JSON-LD as primary source
        product_data = self._extract_from_json_ld_primary(json_ld_data, url)
        
        # Enhance with tool-specific extraction from HTML
        html_data = self._extract_tool_specific_data(html_content, url)
        
        # Merge data, prioritizing JSON-LD for essential fields
        for key, value in html_data.items():
            if key not in product_data or not product_data[key]:
                product_data[key] = value
        
        return product_data
    
    def _extract_from_json_ld_primary(self, json_ld_data: Dict, url: str) -> Dict[str, Any]:
        """Extract primary product data from JSON-LD structured data"""
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_piece': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'InstallationToolPageParser'
        }
        
        # Extract from JSON-LD first (most reliable)
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price - for installation tools, usually per piece
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_piece'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
            
            # Extract description
            if json_ld_data.get('description'):
                product_data['description'] = self._clean_html_text(json_ld_data['description'])
            
            # Extract SKU if not found in URL
            if json_ld_data.get('sku') and not product_data['sku']:
                product_data['sku'] = json_ld_data['sku']
        
        return product_data
    
    def _extract_tool_specific_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract installation tool-specific data from HTML content"""
        tool_data = {
            'quantity': None,
            'weight': None,
            'tool_type': None
        }
        
        content_lower = html_content.lower()
        
        # Extract quantity (pieces per bag/box)
        for pattern in self.extraction_patterns["quantity_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                tool_data['quantity'] = f"{match.group(1)} pieces"
                break
        
        # Extract weight
        for pattern in self.extraction_patterns["weight_patterns"]:
            match = re.search(pattern, content_lower)
            if match:
                tool_data['weight'] = f"{match.group(1)} lbs"
                break
        
        # Identify tool type
        for tool_type in self.extraction_patterns["tool_keywords"]:
            if tool_type in content_lower:
                tool_data['tool_type'] = tool_type.title()
                break
        
        return tool_data

class DefaultPageParser(BaseProductParser):
    """Fallback parser for unknown page types"""
    
    def __init__(self):
        super().__init__(PageType.UNKNOWN)
    
    def _build_extraction_patterns(self) -> Dict[str, Any]:
        return {
            "generic_patterns": [
                r'\$(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)',
                r'(\d+)\s*pieces?'
            ]
        }
    
    def parse_product_data(self, html_content: str, url: str, json_ld_data: Dict = None) -> Dict[str, Any]:
        """Generic parsing for unknown page types"""
        
        # Extract JSON-LD if not provided
        if not json_ld_data:
            json_ld_data = self._extract_json_ld_data(html_content)
        
        # Initialize basic product data
        product_data = {
            'url': url,
            'sku': self._extract_sku_from_url(url),
            'title': None,
            'brand': None,
            'price_per_piece': None,
            'description': None,
            'specifications': {},
            'primary_image': None,
            'parsing_method': 'DefaultPageParser'
        }
        
        # Extract from JSON-LD
        if json_ld_data:
            product_data['title'] = self._clean_html_text(json_ld_data.get('name', ''))
            
            # Extract brand
            brand_info = json_ld_data.get('brand', {})
            if isinstance(brand_info, dict):
                product_data['brand'] = brand_info.get('name', '')
            elif isinstance(brand_info, str):
                product_data['brand'] = brand_info
            
            # Extract price
            offers = json_ld_data.get('offers', {})
            if isinstance(offers, dict) and offers.get('price'):
                try:
                    product_data['price_per_piece'] = float(offers['price'])
                except (ValueError, TypeError):
                    pass
            
            # Extract primary image
            if json_ld_data.get('image'):
                product_data['primary_image'] = json_ld_data['image']
        
        return product_data

def get_parser_for_page_type(page_type: PageType) -> BaseProductParser:
    """Factory function to get appropriate parser for page type"""
    parser_map = {
        PageType.TILE: TilePageParser(),
        PageType.GROUT: GroutPageParser(),
        PageType.TRIM_MOLDING: TrimMoldingPageParser(),
        PageType.LUXURY_VINYL: LuxuryVinylPageParser(),
        PageType.INSTALLATION_TOOL: InstallationToolPageParser(),
        PageType.UNKNOWN: DefaultPageParser()
    }
    
    return parser_map.get(page_type, DefaultPageParser())

def test_specialized_parsers():
    """Test specialized parsers with sample data"""
    print("Testing Specialized Parsers:")
    print("=" * 50)
    
    # Test data for each parser type
    test_cases = [
        {
            "parser": TilePageParser(),
            "content": "Volakas Honed Marble Wall and Floor Tile - 12 x 24 in. Natural marble from Greece. 12.02 sq. ft. per Box. Honed finish. Price: $287.04",
            "url": "https://www.tileshop.com/products/volakas-honed-marble-681294",
            "json_ld": {"name": "Volakas Honed Marble Wall and Floor Tile - 12 x 24 in.", "brand": {"name": "Rush River"}, "offers": {"price": "287.04"}}
        },
        {
            "parser": GroutPageParser(),
            "content": "Superior Sanded Pro-Grout Natural - 25 lb. Sanded grout for tile joints. Color: Grey. Price: $24.29",
            "url": "https://www.tileshop.com/products/superior-sanded-pro-grout-052001",
            "json_ld": {"name": "Superior Sanded Pro-Grout Natural - 25 lb", "brand": {"name": "Superior"}, "offers": {"price": "24.29"}}
        },
        {
            "parser": TrimMoldingPageParser(),
            "content": "T-Molding - 1.77 x 94 in. Box contains 20 pieces. Installation guidelines included. Price: $51.09",
            "url": "https://www.tileshop.com/products/t-molding-682003",
            "json_ld": {"name": "T-Molding - 1.77 x 94 in.", "offers": {"price": "51.09"}}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        parser = test_case["parser"]
        result = parser.parse_product_data(
            test_case["content"], 
            test_case["url"], 
            test_case["json_ld"]
        )
        
        print(f"\n{i}. {parser.__class__.__name__}:")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   SKU: {result.get('sku', 'N/A')}")
        print(f"   Brand: {result.get('brand', 'N/A')}")
        print(f"   Price: ${result.get('price_per_box', result.get('price_per_piece', 'N/A'))}")
        print(f"   Specifications: {len(result.get('specifications', {}))}")
        print(f"   Method: {result.get('parsing_method', 'N/A')}")

if __name__ == "__main__":
    test_specialized_parsers()