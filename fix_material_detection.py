#!/usr/bin/env python3
"""
Fix Material Detection Issues for Tools and Complex Products
"""

from enhanced_categorization_system import EnhancedCategorizer

def create_enhanced_material_detector():
    """Create an enhanced material detector with better tool recognition"""
    
    class ImprovedMaterialDetector(EnhancedCategorizer):
        def extract_material_type(self, product_data):
            """Enhanced material type extraction with tool-specific logic"""
            
            title = product_data.get('title', '').lower()
            description = product_data.get('description', '').lower()
            text_content = f"{title} {description}".lower()
            
            print(f"🔍 Enhanced Material Detection for: {product_data.get('title', 'Unknown')}")
            
            # PRIORITY 1: Tool-specific material detection
            tool_patterns = [
                # Diamond tools
                (['diamond', 'bit'], 'metal', 'Diamond bits are metal with diamond coating'),
                (['diamond', 'drill'], 'metal', 'Diamond drill bits are metal tools'),
                (['diamond', 'polishing'], 'composite', 'Diamond polishing pads are composite materials'),
                (['diamond', 'pad'], 'composite', 'Diamond pads use composite construction'),
                (['diamond', 'cutting'], 'metal', 'Diamond cutting tools are metal-based'),
                
                # Tool materials
                (['countersink', 'bit'], 'metal', 'Countersink bits are metal tools'),
                (['drill', 'bit'], 'metal', 'Drill bits are metal construction'),
                (['polishing', 'pad'], 'composite', 'Polishing pads are composite materials'),
                (['sanding', 'pad'], 'composite', 'Sanding pads are composite materials'),
                (['cutting', 'wheel'], 'composite', 'Cutting wheels are composite abrasive'),
                
                # Fasteners and hardware
                (['screw', 'stainless'], 'metal', 'Stainless steel screws are metal'),
                (['fastener', 'kit'], 'metal', 'Fastener kits are typically metal'),
                (['washer', 'kit'], 'metal', 'Washer kits are metal components'),
                
                # Grout materials
                (['urethane', 'grout'], 'urethane', 'Urethane grout is polymer-based'),
                (['epoxy', 'grout'], 'epoxy', 'Epoxy grout is synthetic polymer'),
                (['glass-filled', 'grout'], 'urethane', 'Glass-filled grout is typically urethane'),
                
                # Trim materials
                (['aluminum', 'trim'], 'metal', 'Aluminum trim is metal'),
                (['anodized', 'profile'], 'metal', 'Anodized profiles are metal'),
                (['stainless', 'trim'], 'metal', 'Stainless steel trim is metal'),
            ]
            
            # Check tool-specific patterns first
            for keywords, material, reasoning in tool_patterns:
                if all(keyword in text_content for keyword in keywords):
                    print(f"  ✅ Tool pattern detected: {material} ({reasoning})")
                    return material
            
            # PRIORITY 2: Brand-specific material knowledge
            brand_materials = {
                'bostik': {
                    'rapidcure': 'urethane',
                    'dimension': 'urethane',
                    'urethane': 'urethane'
                },
                'dural': {
                    'diamond': 'metal',  # Dural Diamond Plus is aluminum
                    'aluminum': 'metal',
                    'anodized': 'metal'
                },
                'wedi': {
                    'board': 'polystyrene',
                    'screw': 'metal',
                    'fastener': 'metal'
                },
                'goboard': {
                    'board': 'polyisocyanurate',
                    'backer': 'polyisocyanurate'
                }
            }
            
            brand = product_data.get('brand', '').lower()
            if brand in brand_materials:
                for keyword, material in brand_materials[brand].items():
                    if keyword in text_content:
                        print(f"  ✅ Brand-specific material: {material} (Brand: {brand}, Keyword: {keyword})")
                        return material
            
            # PRIORITY 3: Call original method but skip misleading patterns
            # Remove problematic content that causes false material detection
            filtered_data = product_data.copy()
            
            # Filter out description content that mentions tile materials when product is a tool
            if any(tool_word in title for tool_word in ['bit', 'pad', 'tool', 'polishing', 'drill', 'saw']):
                # For tools, don't let tile material mentions in description override tool detection
                filtered_description = description
                # Remove mentions of tile materials that are targets, not the tool material
                tile_materials = ['ceramic', 'porcelain', 'glass', 'stone', 'marble', 'granite']
                for tile_mat in tile_materials:
                    if f"{tile_mat} tile" in filtered_description or f"for {tile_mat}" in filtered_description:
                        filtered_description = filtered_description.replace(tile_mat, '')
                
                filtered_data['description'] = filtered_description
                print(f"  🔧 Filtered tool description to prevent false material detection")
            
            # Call parent method with filtered data
            original_result = super().extract_material_type(filtered_data)
            
            if original_result:
                print(f"  ✅ Original detection (filtered): {original_result}")
                return original_result
            
            # PRIORITY 4: Fallback logic for unknown cases
            print(f"  ⚠️ No material detected, using fallback logic")
            
            # Fallback patterns
            if 'grout' in text_content:
                return 'cement'  # Default grout material
            elif any(word in text_content for word in ['bit', 'drill', 'cutting']):
                return 'metal'  # Default tool material
            elif 'polishing' in text_content or 'pad' in text_content:
                return 'composite'  # Default pad material
            elif 'trim' in text_content or 'profile' in text_content:
                return 'metal'  # Default trim material
            
            return None
    
    return ImprovedMaterialDetector()

def test_material_detection_fixes():
    """Test the improved material detection"""
    
    print("🔧 TESTING MATERIAL DETECTION FIXES")
    print("=" * 60)
    
    # Create improved detector
    improved_detector = create_enhanced_material_detector()
    
    # Test cases that were problematic
    test_cases = [
        {
            'title': 'BEST OF EVERYTHING 3 Diamond Countersink Bits - 1.375 in.',
            'description': 'Achieve a smooth, high-end finish on your glass, ceramic or porcelain tiles',
            'brand': 'Best of Everything',
            'expected': 'metal'
        },
        {
            'title': 'BEST OF EVERYTHING DIAMOND 3-Step Dry Polishing Pad - 3-piece',
            'description': 'Keep your tile looking like new with polishing pad set for ceramic and porcelain',
            'brand': 'Best of Everything',
            'expected': 'composite'
        },
        {
            'title': 'Bostik Dimension RapidCure Glass-Filled Urethane Grout Diamond 9 lb',
            'description': 'Glass-filled, pre-mixed urethane grout for superior performance',
            'brand': 'Bostik',
            'expected': 'urethane'
        },
        {
            'title': 'Dural Diamond Plus Gold',
            'description': 'Aluminum trim profile with anodized finish for tile edges',
            'brand': 'Dural',
            'expected': 'metal'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['title']}")
        print("-" * 60)
        
        detected_material = improved_detector.extract_material_type(test_case)
        
        success = detected_material == test_case['expected']
        
        print(f"   Expected: {test_case['expected']}")
        print(f"   Detected: {detected_material}")
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        results.append({
            'title': test_case['title'][:40],
            'expected': test_case['expected'],
            'detected': detected_material,
            'success': success
        })
    
    # Summary table
    print(f"\n📊 MATERIAL DETECTION TEST RESULTS")
    print("=" * 80)
    
    header = f"{'Product':<42} {'Expected':<12} {'Detected':<12} {'Result':<8}"
    print(header)
    print("-" * 80)
    
    success_count = 0
    for result in results:
        status = '✅' if result['success'] else '❌'
        row = f"{result['title']:<42} {result['expected']:<12} {result['detected'] or 'None':<12} {status:<8}"
        print(row)
        if result['success']:
            success_count += 1
    
    print("-" * 80)
    print(f"Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

if __name__ == "__main__":
    test_material_detection_fixes()