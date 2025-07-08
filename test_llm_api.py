#!/usr/bin/env python3
"""
Test LLM API Integration with Correct API Key
"""

from enhanced_specification_extractor import EnhancedSpecificationExtractor
import os

def test_llm_category_detection():
    """Test LLM category detection with proper API key"""
    
    print("🔑 TESTING LLM API INTEGRATION")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✅ API Key found: {api_key[:20]}...")
    else:
        print("❌ No API key found in environment")
        return
    
    # Initialize extractor
    extractor = EnhancedSpecificationExtractor()
    
    # Test products
    test_products = [
        {
            'title': 'BEST OF EVERYTHING 3 Diamond Countersink Bits - 1.375 in.',
            'description': 'Achieve a smooth, high-end finish on your glass, ceramic or porcelain tiles',
            'expected_category': 'Tool'
        },
        {
            'title': 'BEST OF EVERYTHING DIAMOND 3-Step Dry Polishing Pad - 3-piece',
            'description': 'Keep your tile looking like new with polishing pad set',
            'expected_category': 'Tool'
        },
        {
            'title': 'Bostik Dimension RapidCure Glass-Filled Urethane Grout Diamond 9 lb',
            'description': 'Glass-filled, pre-mixed urethane grout for superior performance',
            'expected_category': 'Grout'
        },
        {
            'title': 'Dural Diamond Plus Gold',
            'description': 'Aluminum trim profile with anodized finish for tile edges',
            'expected_category': 'Trim'
        }
    ]
    
    print(f"\n🧪 Testing LLM Category Detection:")
    print("-" * 50)
    
    results = []
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Testing: {product['title']}")
        
        try:
            # Test LLM category detection
            llm_category = extractor._detect_category_with_llm(
                product['title'], 
                product['description']
            )
            
            if llm_category:
                success = llm_category.lower() == product['expected_category'].lower()
                print(f"   Expected: {product['expected_category']}")
                print(f"   Detected: {llm_category}")
                print(f"   Result: {'✅ SUCCESS' if success else '❌ MISMATCH'}")
                
                results.append({
                    'title': product['title'][:40],
                    'expected': product['expected_category'],
                    'detected': llm_category,
                    'success': success
                })
            else:
                print(f"   ❌ No category detected")
                results.append({
                    'title': product['title'][:40],
                    'expected': product['expected_category'],
                    'detected': 'None',
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ LLM Error: {e}")
            results.append({
                'title': product['title'][:40],
                'expected': product['expected_category'],
                'detected': 'Error',
                'success': False
            })
    
    # Results summary
    print(f"\n📊 LLM CATEGORY DETECTION RESULTS")
    print("=" * 80)
    
    header = f"{'Product':<42} {'Expected':<10} {'Detected':<10} {'Result':<8}"
    print(header)
    print("-" * 80)
    
    success_count = 0
    for result in results:
        status = '✅' if result['success'] else '❌'
        row = f"{result['title']:<42} {result['expected']:<10} {result['detected']:<10} {status:<8}"
        print(row)
        if result['success']:
            success_count += 1
    
    print("-" * 80)
    print(f"Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    # API troubleshooting
    if success_count == 0:
        print(f"\n🔧 API TROUBLESHOOTING:")
        print("If all tests failed, try:")
        print("1. export ANTHROPIC_API_KEY=your-key-here")
        print("2. Check if the API key is valid and has credits")
        print("3. Verify network connectivity to Anthropic API")
    else:
        print(f"\n✅ LLM Integration Working!")
        print("The API key export resolved the authentication issues.")

if __name__ == "__main__":
    test_llm_category_detection()