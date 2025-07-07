#!/usr/bin/env python3
"""
Enhanced Specification Extractor for Auto-Expanding Schema
Automatically detects and extracts all available specification fields from product pages
"""

import re
import json
from typing import Dict, Any, List, Tuple

class EnhancedSpecificationExtractor:
    """Auto-expanding specification extractor for comprehensive data capture"""
    
    def __init__(self):
        self.tile_field_patterns = self._build_tile_extraction_patterns()
        self.generic_field_patterns = self._build_generic_patterns()
        
    def _build_tile_extraction_patterns(self) -> Dict[str, List[str]]:
        """Build extraction patterns for tile-specific fields"""
        return {
            # Dimensions & Physical Properties
            "thickness": [
                r'"PDPInfo_Thickness"[^}]*"Value"\s*:\s*"([^"]+)"',
                r'Thickness[:\s]*([0-9.]+\s*mm)',
                r'"thickness"[:\s]*"([^"]+)"',
                r'Thickness:\s*([^<\n,]+)',
            ],
            "box_quantity": [
                r'Box Quantity[:\s]*([0-9]+)',
                r'"boxQuantity"[:\s]*([0-9]+)',
                r'Pieces per Box[:\s]*([0-9]+)',
                r'Quantity per Box[:\s]*([0-9]+)',
            ],
            "box_weight": [
                r'Box Weight[:\s]*([0-9.]+\s*lbs?)',
                r'"boxWeight"[:\s]*"([^"]+)"',
                r'Weight per Box[:\s]*([^<\n,]+)',
            ],
            "edge_type": [
                r'"PDPInfo_EdgeType","Value":"([^"]+)"',  # Tileshop JSON format - PRIORITY
                r'Edge Type[:\s]*([^<\n,]+)',
                r'"edgeType"[:\s]*"([^"]+)"',
                r'Edge[:\s]*([^<\n,]+)',
                r'Rectified[:\s]*(Yes|No)',
            ],
            "shade_variation": [
                r'Shade Variation[:\s]*([VL][0-9])',
                r'"shadeVariation"[:\s]*"([^"]+)"',
                r'Variation[:\s]*([VL][0-9])',
            ],
            "number_of_faces": [
                r'Number of Faces[:\s]*([0-9]+)',
                r'"numberOfFaces"[:\s]*([0-9]+)',
                r'Faces[:\s]*([0-9]+)',
            ],
            "directional_layout": [
                r'Directional Layout[:\s]*(Yes|No)',
                r'"directionalLayout"[:\s]*"([^"]+)"',
                r'Directional[:\s]*(Yes|No)',
            ],
            "country_of_origin": [
                r'Country of Origin[:\s]*([^<\n,]+)',
                r'"countryOfOrigin"[:\s]*"([^"]+)"',
                r'Origin[:\s]*([^<\n,]+)',
                r'Made in[:\s]*([^<\n,]+)',
            ],
            "material_type": [
                r'Material Type[:\s]*([^<\n,]+)',
                r'"materialType"[:\s]*"([^"]+)"',
                r'Material[:\s]*([^<\n,]+)',
            ],
            "slip_resistance": [
                r'Slip Resistance[:\s]*([^<\n,]+)',
                r'"slipResistance"[:\s]*"([^"]+)"',
                r'COF[:\s]*([0-9.]+)',
                r'Coefficient of Friction[:\s]*([0-9.]+)',
            ],
            "water_absorption": [
                r'Water Absorption[:\s]*([^<\n,]+)',
                r'"waterAbsorption"[:\s]*"([^"]+)"',
                r'Absorption[:\s]*([^<\n,]+)',
            ],
            "frost_resistance": [
                r'Frost Resistance[:\s]*([^<\n,]+)',
                r'"frostResistance"[:\s]*"([^"]+)"',
                r'Frost Resistant[:\s]*(Yes|No)',
            ],
            "breaking_strength": [
                r'Breaking Strength[:\s]*([^<\n,]+)',
                r'"breakingStrength"[:\s]*"([^"]+)"',
                r'Strength[:\s]*([^<\n,]+)',
            ],
            "pei_rating": [
                r'PEI Rating[:\s]*([0-5])',
                r'"peiRating"[:\s]*"?([0-5])"?',
                r'PEI[:\s]*([0-5])',
            ],
            "installation_method": [
                r'Installation Method[:\s]*([^<\n,]+)',
                r'"installationMethod"[:\s]*"([^"]+)"',
                r'Installation[:\s]*([^<\n,]+)',
            ],
            "finish": [
                r'"PDPInfo_Finish"[^}]*"Value"\s*:\s*"([^"]+)"',
                r'Finish[:\s]*([^<\n,]+)',
                r'"finish"[:\s]*"([^"]+)"',
                r'Surface Finish[:\s]*([^<\n,]+)',
            ],
            "recommended_grout": [
                r'"PDPInfo_RecommendedGrout"[^}]*"Value"\s*:\s*"([^"]+)"',
                r'Recommended Grout[:\s]*([^<\n,]+)',
                r'"recommendedGrout"[:\s]*"([^"]+)"',
                r'Grout[:\s]*([^<\n,]+)',
            ],
            # Design Properties  
            "texture": [
                r'Texture[:\s]*([^<\n,]+)',
                r'"texture"[:\s]*"([^"]+)"',
                r'Surface[:\s]*([^<\n,]+)',
            ],
            "pattern": [
                r'Pattern[:\s]*([^<\n,]+)', 
                r'"pattern"[:\s]*"([^"]+)"',
            ],
            "style": [
                r'Style[:\s]*([^<\n,]+)',
                r'"style"[:\s]*"([^"]+)"',
                r'Design Style[:\s]*([^<\n,]+)',
            ],
        }
    
    def _build_generic_patterns(self) -> List[str]:
        """Build patterns for auto-detecting unknown specification fields"""
        return [
            # Tileshop-specific PDPInfo patterns - PRIORITY PATTERNS
            r'"PDPInfo_([^"]+)"[^}]*"Value"\s*:\s*"([^"]+)"',
            r'"Key"\s*:\s*"PDPInfo_([^"]+)"[^}]*"Value"\s*:\s*"([^"]+)"',
            
            # Specific field patterns for known issues
            r'"PDPInfo_Thickness"[^}]*"Value"\s*:\s*"([^"]+)"',
            r'"PDPInfo_Finish"[^}]*"Value"\s*:\s*"([^"]+)"',
            r'"PDPInfo_RecommendedGrout"[^}]*"Value"\s*:\s*"([^"]+)"',
            
            # Standard specification patterns
            r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*:\s*([^<\n,]{1,50})',
            
            # JSON-LD structured data patterns (more selective)
            r'"(thickness|weight|quantity|coverage|edge|shade|variation|faces|directional|country|origin|material|type|slip|resistance|water|absorption|frost|breaking|strength|pei|rating|installation|texture|pattern|style|finish|color|application|wear|layer|core|backing|surface|hardness|acoustic|waterproof|size|dimension)"[^:]*:\s*"([^"]+)"',
            
            # HTML table patterns  
            r'<td[^>]*>([^:]+):</td>\s*<td[^>]*>([^<]+)</td>',
            
            # Definition list patterns
            r'<dt[^>]*>([^:]+):</dt>\s*<dd[^>]*>([^<]+)</dd>',
            
            # Specification block patterns
            r'<div[^>]*class="[^"]*spec[^"]*"[^>]*>([^:]+):\s*([^<]+)</div>',
        ]
    
    def extract_specifications(self, html_content: str, category: str = "tile") -> Dict[str, Any]:
        """
        Extract all available specifications from HTML content
        Returns both known fields and auto-detected fields
        """
        print("🔍 Enhanced Specification Extraction")
        print("-" * 40)
        
        specifications = {}
        auto_detected = {}
        
        # 1. Extract known tile-specific fields
        if category.lower() in ['tile', 'tiles', 'ceramic', 'porcelain']:
            specifications.update(self._extract_known_fields(html_content))
        
        # 2. Auto-detect unknown fields
        auto_detected = self._auto_detect_fields(html_content)
        
        # 3. Merge results with priority to known fields
        final_specs = {**auto_detected, **specifications}
        
        # 4. Clean and validate
        final_specs = self._clean_specifications(final_specs)
        
        print(f"✅ Extracted {len(final_specs)} specification fields")
        for field, value in final_specs.items():
            print(f"   {field}: {value}")
        
        return final_specs
    
    def _extract_known_fields(self, html_content: str) -> Dict[str, Any]:
        """Extract known tile specification fields using defined patterns"""
        extracted = {}
        
        for field_name, patterns in self.tile_field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if value and len(value) > 0:
                        # Type conversion for specific fields
                        if field_name in ['box_quantity', 'number_of_faces', 'pei_rating']:
                            try:
                                extracted[field_name] = int(value)
                            except ValueError:
                                extracted[field_name] = value
                        elif field_name == 'directional_layout':
                            extracted[field_name] = value.lower() == 'yes'
                        else:
                            extracted[field_name] = value
                        break
        
        return extracted
    
    def _auto_detect_fields(self, html_content: str) -> Dict[str, str]:
        """Auto-detect specification fields using generic patterns"""
        detected = {}
        
        for pattern in self.generic_field_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    field_name, field_value = match
                    
                    # Clean field name
                    field_name = self._normalize_field_name(field_name)
                    field_value = field_value.strip()
                    
                    # Filter out common false positives
                    if self._is_valid_specification_field(field_name, field_value):
                        detected[field_name] = field_value
        
        return detected
    
    def _normalize_field_name(self, field_name: str) -> str:
        """Normalize field names to consistent format"""
        # Remove HTML tags
        field_name = re.sub(r'<[^>]+>', '', field_name)
        # Convert to lowercase and replace spaces/special chars with underscores
        field_name = re.sub(r'[^\w\s]', '', field_name).strip().lower()
        field_name = re.sub(r'\s+', '_', field_name)
        # Remove leading/trailing underscores
        field_name = field_name.strip('_')
        return field_name
    
    def _is_valid_specification_field(self, field_name: str, field_value: str) -> bool:
        """Check if detected field is a valid specification"""
        # Minimum length requirements
        if len(field_name) < 3 or len(field_value) < 1:
            return False
        
        # Maximum length limits
        if len(field_name) > 50 or len(field_value) > 200:
            return False
        
        # Skip common non-specification patterns and corrupted data
        invalid_patterns = [
            'class', 'id', 'href', 'src', 'alt', 'title', 'data',
            'script', 'style', 'meta', 'link', 'button', 'input',
            'google', 'analytics', 'facebook', 'twitter', 'pinterest',
            'cookie', 'privacy', 'terms', 'policy', 'subscribe',
            'email', 'phone', 'address', 'zip', 'state', 'city',
            'cart', 'order', 'checkout', 'payment', 'shipping',
            'error', 'label', 'message', 'template', 'component',
            'page', 'url', 'path', 'navigation', 'menu', 'footer',
            'header', 'signin', 'register', 'account', 'customer',
            'form', 'field', 'placeholder', 'reward', 'invoice',
            'pdf', 'sample', 'search', 'filter', 'sort', 'tag',
            'default', 'success', 'cancel', 'back', 'next', 'submit',
            'status', 'locale', 'language', 'hostname', 'version'
        ]
        
        # Additional patterns for corrupted/HTML data
        corrupted_patterns = [
            '-care/installation/tools', 'Asset_Grid_All_V2', '_Detail:',
            'Installation Guidelines', 'Samples Sent to', 'Piece Count',
            'Commercial Warranty', 'Frost Resistance', 'Wear Layer', 
            'External Links', 'Image', '/>', 'ed', 'Application',
            'Refresh Project', 'Color', 'Material', 'DesignInstallation'
        ]
        
        field_lower = field_name.lower()
        value_lower = field_value.lower()
        
        # Check field name for invalid patterns
        for invalid in invalid_patterns:
            if invalid in field_lower:
                return False
        
        # Check field value for corrupted patterns
        for corrupted in corrupted_patterns:
            if corrupted.lower() in value_lower:
                return False
        
        # Only allow specification-like field names
        valid_spec_keywords = [
            'thickness', 'weight', 'quantity', 'box', 'coverage', 'edge',
            'shade', 'variation', 'faces', 'directional', 'country', 'origin',
            'material', 'type', 'slip', 'resistance', 'water', 'absorption',
            'frost', 'breaking', 'strength', 'pei', 'rating', 'installation',
            'texture', 'pattern', 'style', 'finish', 'color', 'application',
            'wear', 'layer', 'core', 'backing', 'surface', 'hardness',
            'acoustic', 'waterproof', 'size', 'dimension', 'room', 'look'
        ]
        
        # Check if field name contains any valid specification keywords
        if not any(keyword in field_lower for keyword in valid_spec_keywords):
            return False
        
        # Skip values that look like HTML/URLs/JS
        if any(char in value_lower for char in ['<', '>', '{', '}', 'function', 'var ', 'http', '"']):
            return False
        
        # Skip very long values that are likely descriptions
        if len(field_value) > 100:
            return False
        
        return True
    
    def _clean_specifications(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize specification values"""
        cleaned = {}
        
        for field, value in specifications.items():
            if isinstance(value, str):
                # Remove HTML tags
                value = re.sub(r'<[^>]+>', '', value)
                # Clean whitespace
                value = re.sub(r'\s+', ' ', value).strip()
                # Remove quotes
                value = value.strip('"\'')
                
                # Skip empty values
                if not value or value.lower() in ['n/a', 'na', 'none', '', '-']:
                    continue
                
                cleaned[field] = value
            else:
                cleaned[field] = value
        
        return cleaned
    
    def get_schema_recommendations(self, specifications: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        """Generate database schema recommendations for detected fields"""
        recommendations = []
        
        for field_name, value in specifications.items():
            # Determine appropriate SQL type
            if isinstance(value, int):
                sql_type = "INTEGER"
                description = f"Numeric specification: {field_name}"
            elif isinstance(value, bool):
                sql_type = "BOOLEAN" 
                description = f"Boolean specification: {field_name}"
            elif isinstance(value, str):
                if len(value) <= 20:
                    sql_type = "VARCHAR(50)"
                elif len(value) <= 100:
                    sql_type = "VARCHAR(200)"
                else:
                    sql_type = "TEXT"
                description = f"Text specification: {field_name}"
            else:
                sql_type = "VARCHAR(255)"
                description = f"General specification: {field_name}"
            
            recommendations.append((field_name, sql_type, description))
        
        return recommendations

def test_enhanced_extraction():
    """Test the enhanced specification extractor"""
    extractor = EnhancedSpecificationExtractor()
    
    # Test with sample HTML
    sample_html = """
    <div class="specifications">
        <p>Thickness: 8.7mm</p>
        <p>Box Quantity: 5</p>
        <p>Shade Variation: V3</p>
        <p>Edge Type: Rectified</p>
        <p>Country of Origin: Spain</p>
    </div>
    """
    
    specs = extractor.extract_specifications(sample_html, "tile")
    print(f"Test extracted: {specs}")
    
    recommendations = extractor.get_schema_recommendations(specs)
    print("Schema recommendations:")
    for field, sql_type, desc in recommendations:
        print(f"   {field}: {sql_type} -- {desc}")

if __name__ == "__main__":
    test_enhanced_extraction()