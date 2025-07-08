#!/usr/bin/env python3
"""
Test Web Search Validation System (LLM-independent)
"""

from enhanced_validation_system import LLMValidationSystem

def test_web_search_validation_system():
    """Test the web search validation system independently"""
    
    def mock_web_search(query):
        """Mock web search that returns research-based results"""
        print(f"🌐 Web Search Query: {query}")
        
        query_lower = query.lower()
        
        if 'goboard' in query_lower and 'material' in query_lower:
            return """GoBoard backer boards by Johns Manville are manufactured using polyisocyanurate foam core technology. The polyiso foam provides excellent thermal insulation and moisture resistance properties. The boards feature fiberglass mat facings for structural integrity."""
        
        elif 'superior' in query_lower and 'sealer' in query_lower:
            return """Superior stone sealers are chemical polymer-based protective coatings designed for natural stone surfaces. The formula uses advanced chemical compounds to penetrate stone pores and create a protective barrier against stains and moisture."""
        
        elif 'ardex t-7' in query_lower or ('sponge' in query_lower and 'tile' in query_lower):
            return """Professional tile sponges like the Ardex T-7 are manufactured from synthetic foam materials. These synthetic polymer-based sponges are specifically designed for ceramic and porcelain tile cleaning applications."""
        
        elif 'wedi' in query_lower and ('screw' in query_lower or 'fastener' in query_lower):
            return """Wedi fastening systems use marine-grade stainless steel construction. The screws and washers are manufactured from 316-grade stainless steel for superior corrosion resistance in wet environments."""
        
        return "No specific information found."
    
    # Initialize validation system with web search
    validator = LLMValidationSystem(web_search_tool=mock_web_search)
    
    # Test products with known material composition research
    test_products = [
        {
            'title': 'GoBoard Backer Board 4ft x 8ft x ½ in',
            'material_type': 'composite',  # Low confidence - should trigger research
            'brand': 'GoBoard',
            'product_category': 'Substrate'
        },
        {
            'title': 'Superior Premium Gold Stone Sealer Pint',
            'material_type': 'unknown',  # Low confidence - should trigger research
            'brand': 'Superior',
            'product_category': 'Sealer'
        },
        {
            'title': 'Ardex T-7 Ceramic Tile Sponge',
            'material_type': 'foam',  # Low confidence - should trigger research
            'brand': 'Ardex',
            'product_category': 'Tool'
        },
        {
            'title': 'Wedi Screw and Washer Fastener Kit',
            'material_type': 'hardware',  # Low confidence - should trigger research
            'brand': 'Wedi',
            'product_category': 'Tool'
        }
    ]
    
    print("🧪 Testing Web Search Validation System")
    print("=" * 70)
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Validating: {product['title']}")
        print("-" * 50)
        
        # Run validation
        validation_results = validator.validate_product_data(product)
        
        if validation_results:
            print(f"   📊 Validation Results Found: {len(validation_results)}")
            for result in validation_results:
                print(f"      {result.field}: '{result.original_value}' → '{result.validated_value}'")
                print(f"      Confidence: {result.confidence:.2f}")
                print(f"      Method: {result.validation_method}")
                print(f"      Source: {result.research_source}")
        else:
            print(f"   ✅ No validation needed (high confidence)")
        
        print()

def test_confidence_calculation():
    """Test confidence calculation triggers validation"""
    
    def simple_web_search(query):
        return "Mock research result for validation testing"
    
    validator = LLMValidationSystem(web_search_tool=simple_web_search)
    
    print("\n🎯 Testing Confidence Thresholds")
    print("=" * 50)
    
    # Test different confidence scenarios
    test_cases = [
        {
            'title': 'GoBoard Backer Board',
            'material_type': 'goboard_material',  # Should be high confidence due to brand match
            'brand': 'GoBoard'
        },
        {
            'title': 'Unknown Brand Composite Board',
            'material_type': 'composite',  # Should be low confidence
            'brand': 'Unknown'
        },
        {
            'title': 'Stainless Steel Screw Kit',
            'material_type': 'metal',  # Should be high confidence due to keyword match
            'brand': 'Generic'
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['title']}")
        
        # Calculate confidence for material_type
        confidence = validator._calculate_confidence(
            'material_type', 
            test_case['material_type'], 
            test_case['title']
        )
        
        threshold = validator.confidence_thresholds.get('material_type', 0.8)
        will_research = confidence < threshold
        
        print(f"   Material: {test_case['material_type']}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Threshold: {threshold}")
        print(f"   Will research: {'Yes' if will_research else 'No'}")

if __name__ == "__main__":
    test_web_search_validation_system()
    test_confidence_calculation()