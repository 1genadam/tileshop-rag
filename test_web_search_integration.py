#!/usr/bin/env python3
"""
Test Web Search Integration for Enhanced Categorization System
"""

from enhanced_categorization_system import EnhancedCategorizer

def test_web_search_integration():
    """Test the enhanced categorization with web search integration"""
    
    # Create a mock WebSearch function for testing
    def mock_web_search(query):
        """Mock WebSearch function that simulates real web search responses"""
        print(f"Mock WebSearch called with query: {query}")
        
        query_lower = query.lower()
        
        # Return mock search results based on query content
        if 'goboard' in query_lower and 'material' in query_lower:
            return """GoBoard backer boards are manufactured by Johns Manville and are made of polyisocyanurate foam core with fiberglass mat facing. The polyiso foam provides excellent thermal properties and moisture resistance."""
        
        elif 'superior' in query_lower and 'sealer' in query_lower:
            return """Superior stone sealer is a penetrating chemical sealer designed to protect natural stone surfaces. It uses polymer-based technology to create a protective barrier."""
        
        elif 'ardex t-7' in query_lower:
            return """Ardex T-7 is a professional cleaning sponge made of synthetic materials. It's designed specifically for tile and grout cleaning applications."""
        
        elif 'wedi' in query_lower and 'screw' in query_lower:
            return """Wedi screws and fasteners are made of stainless steel with corrosion-resistant coatings. They are specifically designed for use with Wedi foam boards."""
        
        return "No specific information found for this query."
    
    # Initialize categorizer with web search capability
    categorizer = EnhancedCategorizer(web_search_tool=mock_web_search)
    
    # Test products that should trigger web search validation
    test_products = [
        {
            'title': 'GoBoard Backer Board 4ft x 8ft x ½ in',
            'description': 'Composite backer board features a built-in waterproof membrane',
            'brand': 'GoBoard',
            'sku': '350067'
        },
        {
            'title': 'Superior Premium Gold Stone Sealer Pint',
            'description': 'Professional stone sealer for natural stone protection',
            'brand': 'Superior',
            'sku': '220434'
        },
        {
            'title': 'Ardex T-7 Ceramic Tile Sponge',
            'description': 'Professional cleaning sponge for tile installation',
            'brand': 'Ardex',
            'sku': '12506'
        },
        {
            'title': 'Wedi Screw and Washer Fastener Kit',
            'description': 'Fastener kit for Wedi board installation',
            'brand': 'Wedi',
            'sku': '349133'
        }
    ]
    
    print("🧪 Testing Web Search Integration")
    print("=" * 60)
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Testing: {product['title']}")
        print("-" * 50)
        
        # Test material type detection with validation
        print("\n🔍 Material Type Detection with Web Search Validation:")
        material_type = categorizer.extract_material_type(product)
        print(f"   Result: {material_type}")
        
        # Test category detection 
        print("\n📂 Category Detection:")
        category_info = categorizer.categorize_product(product)
        print(f"   Primary Category: {category_info.primary_category}")
        print(f"   Subcategory: {category_info.subcategory}")
        print(f"   Product Type: {category_info.product_type}")
        
        print("\n" + "=" * 60)

def test_without_web_search():
    """Test the system without web search to compare"""
    print("\n🔄 Testing WITHOUT Web Search (for comparison)")
    print("=" * 60)
    
    # Initialize categorizer without web search
    categorizer = EnhancedCategorizer()
    
    test_product = {
        'title': 'GoBoard Backer Board 4ft x 8ft x ½ in',
        'description': 'Composite backer board features a built-in waterproof membrane',
        'brand': 'GoBoard',
        'sku': '350067'
    }
    
    print(f"Testing: {test_product['title']}")
    material_type = categorizer.extract_material_type(test_product)
    print(f"Material Type (without web search): {material_type}")

if __name__ == "__main__":
    test_web_search_integration()
    test_without_web_search()