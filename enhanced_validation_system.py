#!/usr/bin/env python3
"""
Enhanced Validation System with Internet Research
Validates low-confidence LLM assumptions using web research
"""

import re
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation check"""
    field: str
    original_value: str
    validated_value: str
    confidence: float
    research_source: str
    validation_method: str

class LLMValidationSystem:
    """System to validate LLM assumptions with internet research"""
    
    def __init__(self, web_search_tool=None):
        self.web_search_tool = web_search_tool
        self.confidence_thresholds = {
            'material_type': 0.8,
            'product_category': 0.9,
            'brand': 0.95
        }
        
        # Known high-confidence patterns
        self.high_confidence_patterns = {
            'material_type': {
                'chemical': ['sealer', 'cleaner', 'polish', 'enhancer'],
                'metal': ['screw', 'fastener', 'bolt', 'washer', 'stainless steel'],
                'silicone': ['100% silicone', 'silicone caulk', 'sealant'],
                'cement': ['grout', 'mortar', 'thinset']
            },
            'brand': {
                'Superior': ['superior'],
                'Ardex': ['ardex'],
                'Wedi': ['wedi'],
                'GoBoard': ['goboard']
            }
        }
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate product data and research low-confidence assumptions"""
        validation_results = []
        
        # Get key fields to validate
        fields_to_validate = {
            'material_type': product_data.get('material_type'),
            'product_category': product_data.get('product_category'),
            'brand': product_data.get('brand')
        }
        
        title = product_data.get('title', '')
        
        for field, value in fields_to_validate.items():
            if value:
                confidence = self._calculate_confidence(field, value, title)
                
                if confidence < self.confidence_thresholds.get(field, 0.8):
                    print(f"  🔍 Low confidence for {field}='{value}' (confidence: {confidence:.2f})")
                    
                    # Research this assumption
                    validated_result = self._research_assumption(field, value, title, product_data)
                    
                    if validated_result:
                        validation_results.append(validated_result)
                else:
                    print(f"  ✅ High confidence for {field}='{value}' (confidence: {confidence:.2f})")
        
        return validation_results
    
    def _calculate_confidence(self, field: str, value: str, title: str) -> float:
        """Calculate confidence score for a field-value pair"""
        confidence = 0.5  # Base confidence
        
        title_lower = title.lower()
        value_lower = value.lower()
        
        # Check high-confidence patterns
        if field in self.high_confidence_patterns:
            patterns = self.high_confidence_patterns[field]
            
            if value_lower in patterns:
                keywords = patterns[value_lower]
                matches = sum(1 for keyword in keywords if keyword in title_lower)
                if matches > 0:
                    confidence = min(0.95, 0.7 + (matches * 0.1))
        
        # Brand confidence is high if brand name appears in title
        if field == 'brand' and value_lower in title_lower:
            confidence = 0.95
        
        # Material type confidence based on specific keywords
        if field == 'material_type':
            material_keywords = {
                'chemical': ['sealer', 'cleaner', 'polish'],
                'metal': ['screw', 'fastener', 'bolt', 'washer'],
                'silicone': ['silicone', 'caulk', 'sealant'],
                'polyisocyanurate': ['goboard', 'polyiso'],
                'polystyrene': ['wedi', 'foam board']
            }
            
            if value_lower in material_keywords:
                keywords = material_keywords[value_lower]
                matches = sum(1 for keyword in keywords if keyword in title_lower)
                if matches > 0:
                    confidence = min(0.9, 0.6 + (matches * 0.15))
        
        return confidence
    
    def _research_assumption(self, field: str, value: str, title: str, product_data: Dict) -> Optional[ValidationResult]:
        """Research a low-confidence assumption using web search"""
        
        if not self.web_search_tool:
            return None
        
        print(f"  🌐 Researching {field}='{value}' for product: {title}")
        
        # Construct research query
        query = self._build_research_query(field, value, title, product_data)
        
        try:
            # Perform web search
            search_results = self.web_search_tool(query)
            
            # Analyze search results
            validated_value = self._analyze_search_results(field, value, search_results, title)
            
            if validated_value and validated_value != value:
                print(f"  ✅ Research validation: {field} corrected from '{value}' to '{validated_value}'")
                
                return ValidationResult(
                    field=field,
                    original_value=value,
                    validated_value=validated_value,
                    confidence=0.85,  # Research-based confidence
                    research_source="web_search",
                    validation_method="internet_research"
                )
            elif validated_value == value:
                print(f"  ✅ Research confirms: {field}='{value}'")
                return ValidationResult(
                    field=field,
                    original_value=value,
                    validated_value=value,
                    confidence=0.9,  # Confirmed by research
                    research_source="web_search",
                    validation_method="internet_confirmation"
                )
            else:
                print(f"  ⚠️ Research inconclusive for {field}='{value}'")
                
        except Exception as e:
            print(f"  ❌ Research failed for {field}: {e}")
        
        return None
    
    def _build_research_query(self, field: str, value: str, title: str, product_data: Dict) -> str:
        """Build a research query for web search"""
        
        brand = product_data.get('brand', '')
        
        if field == 'material_type':
            # Research material composition
            if brand and brand.lower() in title.lower():
                return f"{brand} {title.split()[0]} material composition what is made of 2024"
            else:
                return f"{title} material composition what is made of 2024"
                
        elif field == 'product_category':
            # Research product type/category
            return f"{title} product category type function 2024"
            
        elif field == 'brand':
            # Research brand/manufacturer
            return f"{title} manufacturer brand who makes 2024"
        
        return f"{title} specifications 2024"
    
    def _analyze_search_results(self, field: str, original_value: str, search_results: str, title: str) -> Optional[str]:
        """Analyze search results to validate or correct the assumption"""
        
        if not search_results:
            return None
        
        search_text = search_results.lower()
        title_keywords = [word.lower() for word in title.split() if len(word) > 2]
        
        if field == 'material_type':
            return self._analyze_material_from_search(search_text, title_keywords)
        elif field == 'brand':
            return self._analyze_brand_from_search(search_text, title_keywords)
        elif field == 'product_category':
            return self._analyze_category_from_search(search_text, title_keywords)
        
        return None
    
    def _analyze_material_from_search(self, search_text: str, title_keywords: List[str]) -> Optional[str]:
        """Analyze search results for material type information"""
        
        # Material patterns to look for in search results
        material_indicators = {
            'polyisocyanurate': ['polyisocyanurate', 'polyiso', 'polyiso foam', 'rigid foam'],
            'polystyrene': ['polystyrene', 'foam board', 'xps', 'extruded polystyrene'],
            'composite': ['composite', 'composite material', 'fiberglass', 'reinforced'],
            'metal': ['stainless steel', 'aluminum', 'galvanized', 'metal', 'steel'],
            'silicone': ['silicone', '100% silicone', 'silicone-based'],
            'chemical': ['chemical', 'polymer', 'synthetic compound'],
            'cement': ['cement', 'portland cement', 'mortar', 'concrete'],
            'ceramic': ['ceramic', 'clay', 'fired clay'],
            'porcelain': ['porcelain', 'vitrified', 'porcelain clay']
        }
        
        # Score each material based on search result mentions
        material_scores = {}
        
        for material, indicators in material_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in search_text:
                    score += search_text.count(indicator)
            
            if score > 0:
                material_scores[material] = score
        
        # Return the highest scoring material if it's significantly higher
        if material_scores:
            best_material = max(material_scores, key=material_scores.get)
            best_score = material_scores[best_material]
            
            # Only return if there's a clear winner
            if best_score >= 2:
                return best_material
        
        return None
    
    def _analyze_brand_from_search(self, search_text: str, title_keywords: List[str]) -> Optional[str]:
        """Analyze search results for brand information"""
        
        # Common brand patterns
        brand_patterns = [
            r'manufactured by ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'made by ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+) manufactures',
            r'([A-Z][a-z]+) brand',
            r'([A-Z][a-z]+)®',
            r'([A-Z][a-z]+)™'
        ]
        
        for pattern in brand_patterns:
            matches = re.findall(pattern, search_text)
            for match in matches:
                brand = match.strip()
                if len(brand) > 2 and brand not in ['The', 'And', 'For', 'With']:
                    return brand
        
        return None
    
    def _analyze_category_from_search(self, search_text: str, title_keywords: List[str]) -> Optional[str]:
        """Analyze search results for product category information"""
        
        # Category indicators in search results
        category_indicators = {
            'Substrate': ['backer board', 'substrate', 'underlayment', 'backing'],
            'Tool': ['tool', 'installation tool', 'accessory', 'hardware'],
            'Sealer': ['sealer', 'sealant', 'waterproofing', 'protection'],
            'Adhesive': ['adhesive', 'mortar', 'bonding agent', 'cement'],
            'Grout': ['grout', 'grouting', 'joint filler'],
            'Tile': ['tile', 'flooring', 'wall covering'],
            'Trim': ['trim', 'molding', 'edge', 'finishing']
        }
        
        # Score each category
        category_scores = {}
        
        for category, indicators in category_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in search_text:
                    score += search_text.count(indicator)
            
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            return best_category
        
        return None

def test_validation_system():
    """Test the validation system"""
    
    # Mock web search function
    def mock_web_search(query):
        # Return mock search results based on query
        if 'goboard' in query.lower():
            return "GoBoard is made of polyisocyanurate foam core with fiberglass mat facing. Johns Manville manufactures GoBoard backer boards using polyiso technology."
        elif 'superior' in query.lower() and 'sealer' in query.lower():
            return "Superior stone sealer is a chemical polymer-based protective coating. Superior Brand manufactures stone care products."
        return ""
    
    validator = LLMValidationSystem(web_search_tool=mock_web_search)
    
    # Test product data
    test_product = {
        'title': 'GoBoard Backer Board 4ft x 8ft',
        'material_type': 'composite',  # Low confidence assumption
        'brand': 'GoBoard',
        'product_category': 'Substrate'
    }
    
    results = validator.validate_product_data(test_product)
    
    print("Validation Results:")
    for result in results:
        print(f"  {result.field}: {result.original_value} → {result.validated_value} (confidence: {result.confidence})")

if __name__ == "__main__":
    test_validation_system()