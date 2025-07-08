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
                r'"Key"\s*:\s*"PDPInfo_BoxQuantity"[^}]*"Value"\s*:\s*"([^"]+)"',  # Tileshop JSON format - PRIORITY
                r'"PDPInfo_BoxQuantity"[^}]*"Value"\s*:\s*"([^"]+)"',  # Alternative format
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
                r'"Key"\s*:\s*"PDPInfo_MaterialType"[^}]*"Value"\s*:\s*"([^"]+)"',  # Tileshop JSON format - PRIORITY
                r'"PDPInfo_MaterialType"[^}]*"Value"\s*:\s*"([^"]+)"',  # Alternative format
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
    
    def extract_specifications(self, html_content: str, category: str = "tile", product_title: str = "") -> Dict[str, Any]:
        """
        Extract all available specifications from HTML content
        Returns both known fields and auto-detected fields
        """
        print("🔍 Enhanced Specification Extraction")
        print("-" * 40)
        
        specifications = {}
        auto_detected = {}
        
        # 1. Extract from __NEXT_DATA__ JSON (highest priority - most accurate)
        next_data_specs = self._extract_from_next_data(html_content)
        specifications.update(next_data_specs)
        
        # 2. Extract known tile-specific fields
        if category.lower() in ['tile', 'tiles', 'ceramic', 'porcelain']:
            specifications.update(self._extract_known_fields(html_content))
        
        # 3. Auto-detect unknown fields
        auto_detected = self._auto_detect_fields(html_content)
        
        # 4. Extract product category from title if provided
        if product_title:
            product_category = self._extract_category_from_title(product_title)
            if product_category:
                specifications['product_category'] = product_category
        
        # 5. Merge results with priority to __NEXT_DATA__, then known fields, then auto-detected
        final_specs = {**auto_detected, **specifications}
        
        # 5. Clean and validate
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
    
    def _extract_from_next_data(self, html_content: str) -> Dict[str, str]:
        """Extract specifications from __NEXT_DATA__ JSON structure"""
        extracted = {}
        
        try:
            # Find __NEXT_DATA__ script tag
            next_data_pattern = r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>'
            match = re.search(next_data_pattern, html_content)
            
            if match:
                next_data_json = match.group(1)
                data = json.loads(next_data_json)
                
                # Navigate to specifications
                specs_path = data.get('props', {}).get('pageProps', {}).get('layoutData', {}).get('sitecore', {}).get('context', {}).get('productData', {}).get('Specifications', {})
                
                # Extract from PDPInfo_DesignInstallation array
                design_installation = specs_path.get('PDPInfo_DesignInstallation', [])
                if isinstance(design_installation, list):
                    for spec_item in design_installation:
                        if isinstance(spec_item, dict) and 'Key' in spec_item and 'Value' in spec_item:
                            key = spec_item['Key']
                            value = spec_item['Value']
                            
                            # Map PDPInfo keys to our field names
                            field_mapping = {
                                'PDPInfo_MaterialType': 'material_type',
                                'PDPInfo_EdgeType': 'edge_type',
                                'PDPInfo_Color': 'color',
                                'PDPInfo_Finish': 'finish',
                                'PDPInfo_Applications': 'applications',
                                'PDPInfo_DirectionalLayout': 'directional_layout'
                            }
                            
                            if key in field_mapping:
                                field_name = field_mapping[key]
                                extracted[field_name] = value
                                print(f"  ✅ __NEXT_DATA__ extracted: {field_name} = {value}")
                
                # Extract from PDPInfo_Dimensions array
                dimensions = specs_path.get('PDPInfo_Dimensions', [])
                if isinstance(dimensions, list):
                    for spec_item in dimensions:
                        if isinstance(spec_item, dict) and 'Key' in spec_item and 'Value' in spec_item:
                            key = spec_item['Key']
                            value = spec_item['Value']
                            
                            field_mapping = {
                                'PDPInfo_BoxQuantity': 'box_quantity',
                                'PDPInfo_BoxWeight': 'box_weight',
                                'PDPInfo_Thickness': 'thickness',
                                'PDPInfo_ApproximateSize': 'approximate_size'
                            }
                            
                            if key in field_mapping:
                                field_name = field_mapping[key]
                                extracted[field_name] = value
                                print(f"  ✅ __NEXT_DATA__ extracted: {field_name} = {value}")
                
                # Extract from PDPInfo_TechnicalDetails array
                technical = specs_path.get('PDPInfo_TechnicalDetails', [])
                if isinstance(technical, list):
                    for spec_item in technical:
                        if isinstance(spec_item, dict) and 'Key' in spec_item and 'Value' in spec_item:
                            key = spec_item['Key']
                            value = spec_item['Value']
                            
                            field_mapping = {
                                'PDPInfo_CountryOfOrigin': 'country_of_origin'
                            }
                            
                            if key in field_mapping:
                                field_name = field_mapping[key]
                                extracted[field_name] = value
                                print(f"  ✅ __NEXT_DATA__ extracted: {field_name} = {value}")
        
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            print(f"  ⚠️ __NEXT_DATA__ extraction failed: {e}")
        
        return extracted
    
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
        
        # Enhanced patterns for corrupted/HTML data and erroneous parsing
        corrupted_patterns = [
            # HTML fragment patterns
            '-care/installation/tools', 'Asset_Grid_All_V2', '_Detail:', '/>', '<',
            'Installation Guidelines', 'Samples Sent to', 'Piece Count',
            'Commercial Warranty', 'Frost Resistance', 'Wear Layer', 
            'External Links', 'Image', 'Application',
            'Refresh Project', 'DesignInstallation',
            
            # Specific erroneous patterns you identified
            '-care/installation/tools">', '_Detail:Asset_Grid_All_V2"}',
            'by pairing this tile with', 'texture_Detail:Asset_Grid_All_V2',
            
            # HTML tag fragments and malformed JSON
            '"}', '{"', '":"', '"Value":', '"Key":',
            'class="', 'id="', 'src="', 'href="', 'alt="',
            
            # URL fragments and file paths
            'http://', 'https://', '.com/', '.html', '.jsp', '.php',
            '/assets/', '/images/', '/static/', '/content/',
            
            # JavaScript/CSS fragments
            'function(', 'var ', 'return ', '$(', 'window.',
            '.css', '.js', 'px;', 'margin:', 'padding:',
            
            # Empty or meaningless values
            'null', 'undefined', 'none', 'n/a', 'tbd', 'tba'
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
        
        # Enhanced validation for malformed data patterns
        
        # Skip values that look like HTML/URLs/JS/JSON fragments
        malformed_indicators = ['<', '>', '{', '}', 'function', 'var ', 'http', '"', '/>', '_Detail:', 'Asset_Grid']
        if any(indicator in value_lower for indicator in malformed_indicators):
            return False
        
        # Skip values with excessive special characters (indicates HTML/JS fragments)
        special_char_count = sum(1 for char in field_value if not char.isalnum() and char not in ' .-_')
        if special_char_count > 3:  # Allow some special chars but not excessive
            return False
        
        # Skip values that are obviously HTML fragments or partial sentences
        html_fragment_patterns = [
            r'by pairing this tile',  # Partial sentences from descriptions
            r'care/installation',     # URL fragments
            r'Asset_Grid_All',        # Asset reference fragments
            r'\w+_Detail:',          # Malformed JSON keys
            r'/>\s*$',               # HTML closing tags
            r'^\s*\{',               # JSON fragments
            r'\}\s*$',               # JSON fragments
        ]
        
        for pattern in html_fragment_patterns:
            if re.search(pattern, field_value, re.IGNORECASE):
                return False
        
        # Skip very long values that are likely descriptions or malformed content
        if len(field_value) > 100:
            return False
        
        # Additional check: skip single-character or obviously incomplete values
        if len(field_value.strip()) < 2:
            return False
        
        return True
    
    def _extract_category_from_title(self, product_title: str) -> str:
        """Extract product category from title"""
        title_lower = product_title.lower()
        
        # Category keywords mapping
        category_keywords = {
            'tile': ['tile', 'tiles', 'ceramic', 'porcelain', 'mosaic', 'subway'],
            'grout': ['grout', 'grouting'],
            'trim': ['trim', 'bullnose', 'edge', 'corner', 'gl', 'great lakes', 'l-channel', 'round edge', 'box edge', 'somerset', 'durand', 'quarter round', 'quarter-round', 'pencil liner', 'liner'],
            'adhesive': ['adhesive', 'mortar', 'cement'],
            'sealer': ['sealer', 'sealant'],
            'tool': ['tool', 'tools', 'cutter', 'spacer'],
            'accessory': ['accessory', 'accessories']
        }
        
        # Check for category keywords in title (prioritize specific terms over generic ones)
        # Priority order: trim > grout > tool > adhesive > sealer > accessory > tile
        priority_order = ['trim', 'grout', 'tool', 'adhesive', 'sealer', 'accessory', 'tile']
        
        for category in priority_order:
            if category in category_keywords:
                keywords = category_keywords[category]
                if any(keyword in title_lower for keyword in keywords):
                    return category.title()
        
        # Default fallback
        return "Product"
    
    def _clean_specifications(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize specification values with corruption filtering"""
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
                
                # Allow valid edge type values regardless of other validation
                if field.lower() in ['edge_type', 'edgetype'] and value.lower() in ['rectified', 'pressed', 'natural', 'polished']:
                    cleaned[field] = value
                    continue
                
                # Allow valid product category values regardless of other validation
                if field.lower() in ['product_category', 'category'] and value.lower() in ['tile', 'tiles', 'grout', 'trim', 'adhesive', 'sealer', 'tool', 'accessory', 'product']:
                    cleaned[field] = value
                    continue
                
                # Apply pattern logic BEFORE corruption filtering for pattern fields
                if field.lower() in ['pattern', 'has_pattern']:
                    # Convert pattern descriptions to Yes/No
                    pattern_indicators = ['pattern', 'pairing', 'combine', 'mix', 'match', 'coordinate']
                    has_pattern = any(indicator in value.lower() for indicator in pattern_indicators)
                    value = 'Yes' if has_pattern else 'No'
                    print(f"  🔄 Pattern logic applied: {field} = {value}")
                
                # Apply corruption filtering - USE EXISTING VALIDATION
                elif not self._is_valid_specification_field(field, value):
                    print(f"  🚫 Filtered corrupted data: {field} = {value}")
                    continue
                
                cleaned[field] = value
            else:
                cleaned[field] = value
        
        # Remove duplicate edge type fields - keep only 'edge_type', remove 'edgetype'
        if 'edgetype' in cleaned and 'edge_type' in cleaned:
            print(f"  🔄 Removing duplicate: edgetype = {cleaned['edgetype']} (keeping edge_type)")
            del cleaned['edgetype']
        
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

def analyze_successful_sku_patterns(database_connection=None):
    """
    Analyze successfully processed SKUs to identify valid field patterns
    This helps improve validation by understanding what good data looks like
    """
    print("🔍 Analyzing successful SKU patterns for validation improvement")
    print("=" * 60)
    
    if not database_connection:
        print("⚠️  Database connection required for pattern analysis")
        return
    
    try:
        # Query successful SKUs with specifications
        query = """
        SELECT sku, specifications 
        FROM product_data 
        WHERE specifications IS NOT NULL 
        AND json_typeof(specifications) = 'object'
        ORDER BY RANDOM() 
        LIMIT 20
        """
        
        cursor = database_connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        field_patterns = {}
        
        for sku, specs_json in results:
            try:
                if isinstance(specs_json, str):
                    specs = json.loads(specs_json)
                else:
                    specs = specs_json
                
                print(f"\n📋 SKU {sku} - Valid patterns:")
                for field, value in specs.items():
                    if field not in field_patterns:
                        field_patterns[field] = []
                    field_patterns[field].append(str(value))
                    print(f"   {field}: {value}")
                    
            except json.JSONDecodeError:
                continue
        
        print(f"\n📊 Pattern Summary:")
        print("=" * 40)
        for field, values in field_patterns.items():
            unique_values = list(set(values))[:5]  # Show first 5 unique values
            print(f"{field}: {unique_values}")
            
    except Exception as e:
        print(f"❌ Error analyzing patterns: {e}")

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