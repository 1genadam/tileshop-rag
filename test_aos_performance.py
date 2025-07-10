#!/usr/bin/env python3
"""
Test AOS Performance Against Sample Conversation
Target: 4/4 on every AOS phase
"""

import requests
import json
import time

def test_aos_conversation():
    """Test conversation following exact sample conversation flow"""
    
    print("🎯 TESTING AOS PERFORMANCE - TARGET: 4/4 ON EVERY STEP")
    print("=" * 60)
    
    # Sample conversation messages from AOS_SAMPLE_CONVERSATION.md
    test_messages = [
        {
            "message": "hi i'm looking for kitchen floor tile",
            "expected_aos": {
                "phase": "greeting_credibility",
                "should_ask_name": True,
                "should_build_credibility": True,
                "should_explain_process": True
            }
        },
        {
            "message": "my name is Sarah and my phone is 847-302-2594",
            "expected_aos": {
                "phase": "needs_assessment", 
                "should_ask_dimensions": True,
                "should_ask_what_questions": True
            }
        },
        {
            "message": "the kitchen is 8 feet by 10 feet, we have black countertops and white cabinets",
            "expected_aos": {
                "phase": "needs_assessment",
                "should_ask_who_when_how_much": True,
                "should_not_search_products_yet": True
            }
        },
        {
            "message": "we have a contractor, our budget is around $1000, we want to start next week",
            "expected_aos": {
                "phase": "design_details",
                "should_present_tile_bomb": True,
                "should_calculate_requirements": True,
                "requirements_met": True
            }
        }
    ]
    
    conversation_history = []
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"\n🔍 TEST {i}: {test_case['message']}")
        print(f"Expected Phase: {test_case['expected_aos']['phase']}")
        print("-" * 50)
        
        # Send message to API
        try:
            response = requests.post(
                'http://localhost:8080/api/chat/simple',
                json={
                    "query": test_case["message"],
                    "conversation_history": conversation_history
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Display response
                print(f"✅ RESPONSE: {result.get('response')[:200]}...")
                
                # Analyze tools used
                tool_calls = result.get('tool_calls', [])
                print(f"🔧 TOOLS USED: {[tc.get('tool') for tc in tool_calls]}")
                
                # Check AOS compliance
                check_aos_compliance(test_case, result, i)
                
                # Add to conversation history
                conversation_history.extend([
                    {"role": "user", "content": test_case["message"]},
                    {"role": "assistant", "content": result["response"]}
                ])
                
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        print("\n" + "="*60)
        time.sleep(1)  # Brief pause between tests

def check_aos_compliance(test_case, result, test_number):
    """Check if response meets AOS requirements"""
    
    response_text = result.get('response', '').lower()
    expected = test_case['expected_aos']
    compliance_score = 0
    total_checks = 0
    
    print(f"📊 AOS COMPLIANCE CHECK:")
    
    # Test 1: Greeting & Credibility
    if test_number == 1:
        total_checks = 3
        
        if expected.get('should_ask_name') and ('name' in response_text or 'may i have' in response_text):
            print("✅ Asks for customer name")
            compliance_score += 1
        else:
            print("❌ Should ask for customer name")
        
        if expected.get('should_build_credibility') and ('years' in response_text or 'experience' in response_text or 'helped' in response_text):
            print("✅ Builds credibility with experience")
            compliance_score += 1
        else:
            print("❌ Should build credibility with experience")
        
        if expected.get('should_explain_process') and ('process' in response_text or 'walk you through' in response_text):
            print("✅ Explains process")
            compliance_score += 1
        else:
            print("❌ Should explain the process")
    
    # Test 2: Name & Phone Collection
    elif test_number == 2:
        total_checks = 2
        
        if expected.get('should_ask_dimensions') and ('dimensions' in response_text or 'measurements' in response_text or 'length' in response_text):
            print("✅ Asks for dimensions (CRITICAL)")
            compliance_score += 1
        else:
            print("❌ Should ask for dimensions (CRITICAL FAILURE)")
        
        if expected.get('should_ask_what_questions') and any(word in response_text for word in ['color', 'style', 'cabinets', 'countertops']):
            print("✅ Asks WHAT questions")
            compliance_score += 1
        else:
            print("❌ Should ask WHAT questions")
    
    # Test 3: Dimensions & Color Scheme
    elif test_number == 3:
        total_checks = 3
        
        # Check if it asks WHO/WHEN/HOW MUCH questions
        if expected.get('should_ask_who_when_how_much'):
            who_asked = any(word in response_text for word in ['contractor', 'install', 'who'])
            when_asked = any(word in response_text for word in ['start', 'timeline', 'when'])
            how_much_asked = any(word in response_text for word in ['budget', 'cost', 'price'])
            
            if who_asked:
                print("✅ Asks WHO questions")
                compliance_score += 0.33
            else:
                print("❌ Should ask WHO questions")
                
            if when_asked:
                print("✅ Asks WHEN questions") 
                compliance_score += 0.33
            else:
                print("❌ Should ask WHEN questions")
                
            if how_much_asked:
                print("✅ Asks HOW MUCH questions")
                compliance_score += 0.34
            else:
                print("❌ Should ask HOW MUCH questions")
        
        # Check that it doesn't search products yet
        tool_calls = result.get('tool_calls', [])
        if not any(tc.get('tool') == 'search_products' for tc in tool_calls):
            print("✅ Correctly does NOT search products yet")
            compliance_score += 1
        else:
            print("❌ Should NOT search products without complete information")
        
        total_checks = 2
    
    # Test 4: Complete Information
    elif test_number == 4:
        total_checks = 3
        
        # Check for tile bomb presentation
        tool_calls = result.get('tool_calls', [])
        if any(tc.get('tool') == 'search_products' for tc in tool_calls):
            print("✅ Proceeds to product search (requirements met)")
            compliance_score += 1
        else:
            print("❌ Should search products when requirements are met")
        
        # Check for calculations
        if any(tc.get('tool') == 'calculate_project_requirements' for tc in tool_calls):
            print("✅ Performs professional calculations")
            compliance_score += 1
        else:
            print("❌ Should perform project calculations")
        
        # Check for close attempt
        if any(word in response_text for word in ['order', 'move forward', 'go ahead', 'place']):
            print("✅ Attempts to close")
            compliance_score += 1
        else:
            print("❌ Should attempt to close")
    
    # Calculate performance score
    performance = (compliance_score / total_checks) * 4 if total_checks > 0 else 0
    print(f"📈 AOS PERFORMANCE: {performance:.1f}/4 ({compliance_score}/{total_checks} checks passed)")
    
    if performance >= 3.5:
        print("🏆 EXCELLENT PERFORMANCE!")
    elif performance >= 3.0:
        print("✅ GOOD PERFORMANCE")
    elif performance >= 2.0:
        print("⚠️ NEEDS IMPROVEMENT")
    else:
        print("❌ POOR PERFORMANCE - REQUIRES IMMEDIATE ATTENTION")

if __name__ == "__main__":
    test_aos_conversation()