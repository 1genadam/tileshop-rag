#!/usr/bin/env python3
"""
Comprehensive AOS Conversation Test
Tests the complete AOS methodology as per aos_sales_training.md
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

def test_api_call(endpoint, data):
    """Make API call and return response"""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def print_response(phase, query, response_data):
    """Print formatted response"""
    print(f"\n{'='*80}")
    print(f"AOS PHASE: {phase}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    if response_data and response_data.get('success'):
        print(f"RESPONSE: {response_data.get('response', 'No response')}")
        print(f"AOS PHASE: {response_data.get('aos_phase', 'Unknown')}")
        print(f"COLLECTED INFO: {response_data.get('collected_info', {})}")
        print(f"CUSTOMER ID: {response_data.get('customer_id', 'Anonymous')}")
        print(f"CONVERSATION SAVED: {response_data.get('conversation_saved', False)}")
        print(f"KNOWLEDGE USED: {response_data.get('knowledge_used', False)}")
        print(f"VECTORIZATION ELIGIBLE: {response_data.get('vectorization_eligible', False)}")
    else:
        print(f"ERROR: {response_data.get('error', 'Unknown error') if response_data else 'No response'}")

def test_conversation_history(phone_number):
    """Test conversation history retrieval"""
    print(f"\n{'='*80}")
    print(f"TESTING CONVERSATION HISTORY FOR: {phone_number}")
    print(f"{'='*80}")
    
    try:
        # Get conversation history
        response = requests.get(f"{BASE_URL}/api/conversations/history/{phone_number}")
        history_data = response.json()
        
        print(f"HISTORY SUCCESS: {history_data.get('success', False)}")
        if history_data.get('success'):
            conversations = history_data.get('conversations', [])
            print(f"CONVERSATIONS FOUND: {len(conversations)}")
            for i, conv in enumerate(conversations):
                print(f"  {i+1}. Date: {conv.get('conversation_date')}")
                print(f"     Turns: {conv.get('turn_count')}")
                print(f"     Phase: {conv.get('final_phase')}")
                print(f"     Score: {conv.get('overall_score')}")
                print(f"     Outcome: {conv.get('outcomes')}")
        else:
            print(f"HISTORY ERROR: {history_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"HISTORY API ERROR: {e}")

def main():
    """Run comprehensive AOS conversation test"""
    print("🎯 COMPREHENSIVE AOS CONVERSATION TEST")
    print("Following aos_sales_training.md methodology")
    print(f"Started at: {datetime.now()}")
    
    # Test customer information
    phone_number = "555-123-4567"
    first_name = "Mike"
    
    # Test conversation flow
    conversation_data = {
        "phone_number": phone_number,
        "first_name": first_name
    }
    
    # 1. GREETING & CREDIBILITY PHASE
    print("\n🏁 PHASE 1: GREETING & CREDIBILITY")
    query1 = "Hello, I'm Mike. I'm looking at redoing my kitchen backsplash."
    conversation_data["query"] = query1
    response1 = test_api_call("/api/chat/unified", conversation_data)
    print_response("GREETING", query1, response1)
    
    time.sleep(1)
    
    # 2. NEEDS ASSESSMENT PHASE - WHAT
    print("\n📋 PHASE 2: NEEDS ASSESSMENT - WHAT")
    query2 = "It's a kitchen backsplash, about 8 feet long and 18 inches high. I want something modern looking."
    conversation_data["query"] = query2
    response2 = test_api_call("/api/chat/unified", conversation_data)
    print_response("NEEDS ASSESSMENT - WHAT", query2, response2)
    
    time.sleep(1)
    
    # 3. NEEDS ASSESSMENT PHASE - WHO
    print("\n👤 PHASE 3: NEEDS ASSESSMENT - WHO")
    query3 = "I'm planning to install it myself. I've done some tile work before."
    conversation_data["query"] = query3
    response3 = test_api_call("/api/chat/unified", conversation_data)
    print_response("NEEDS ASSESSMENT - WHO", query3, response3)
    
    time.sleep(1)
    
    # 4. NEEDS ASSESSMENT PHASE - WHEN
    print("\n📅 PHASE 4: NEEDS ASSESSMENT - WHEN")
    query4 = "I'm hoping to get this done within the next two weeks."
    conversation_data["query"] = query4
    response4 = test_api_call("/api/chat/unified", conversation_data)
    print_response("NEEDS ASSESSMENT - WHEN", query4, response4)
    
    time.sleep(1)
    
    # 5. NEEDS ASSESSMENT PHASE - HOW MUCH
    print("\n💰 PHASE 5: NEEDS ASSESSMENT - HOW MUCH")
    query5 = "My budget is around $200-300 for the tile."
    conversation_data["query"] = query5
    response5 = test_api_call("/api/chat/unified", conversation_data)
    print_response("NEEDS ASSESSMENT - HOW MUCH", query5, response5)
    
    time.sleep(1)
    
    # 6. DESIGN & DETAILS PHASE - Product Search
    print("\n🎨 PHASE 6: DESIGN & DETAILS - PRODUCT SEARCH")
    query6 = "Show me some subway tile options for a modern kitchen backsplash"
    conversation_data["query"] = query6
    response6 = test_api_call("/api/chat/unified", conversation_data)
    print_response("DESIGN & DETAILS", query6, response6)
    
    time.sleep(1)
    
    # 7. DESIGN & DETAILS PHASE - Specific Product
    print("\n🔍 PHASE 7: DESIGN & DETAILS - SPECIFIC PRODUCT")
    query7 = "Tell me more about the Metro White Subway tile. What are the specifications?"
    conversation_data["query"] = query7
    response7 = test_api_call("/api/chat/unified", conversation_data)
    print_response("DESIGN & DETAILS - SPECIFIC", query7, response7)
    
    time.sleep(1)
    
    # 8. OBJECTION HANDLING PHASE
    print("\n🤔 PHASE 8: OBJECTION HANDLING")
    query8 = "I'm concerned about the price. That seems expensive for subway tile."
    conversation_data["query"] = query8
    response8 = test_api_call("/api/chat/unified", conversation_data)
    print_response("OBJECTION HANDLING", query8, response8)
    
    time.sleep(1)
    
    # 9. DESIGN PHASE - 9F CHECKLIST
    print("\n📝 PHASE 9: 9F CHECKLIST")
    query9 = "What accessories and trim pieces do I need for this installation?"
    conversation_data["query"] = query9
    response9 = test_api_call("/api/chat/unified", conversation_data)
    print_response("9F CHECKLIST", query9, response9)
    
    time.sleep(1)
    
    # 10. CLOSE PHASE
    print("\n🤝 PHASE 10: CLOSE")
    query10 = "I like the Metro White. Can you calculate exactly what I need and give me pricing?"
    conversation_data["query"] = query10
    response10 = test_api_call("/api/chat/unified", conversation_data)
    print_response("CLOSE", query10, response10)
    
    time.sleep(1)
    
    # 11. FINAL CLOSE
    print("\n✅ PHASE 11: FINAL CLOSE")
    query11 = "That looks good. How do I place this order?"
    conversation_data["query"] = query11
    response11 = test_api_call("/api/chat/unified", conversation_data)
    print_response("FINAL CLOSE", query11, response11)
    
    # Test conversation history
    print("\n📚 TESTING CONVERSATION HISTORY")
    test_conversation_history(phone_number)
    
    # Test with second customer for comparison
    print("\n👥 TESTING SECOND CUSTOMER")
    phone_number2 = "555-987-6543"
    first_name2 = "Sarah"
    
    query12 = "Hi, I need tile for my bathroom floor renovation"
    conversation_data2 = {
        "query": query12,
        "phone_number": phone_number2,
        "first_name": first_name2
    }
    response12 = test_api_call("/api/chat/unified", conversation_data2)
    print_response("SECOND CUSTOMER", query12, response12)
    
    # Test database scaling
    print("\n📊 TESTING DATABASE SCALING")
    try:
        # Check database stats
        response = requests.get(f"{BASE_URL}/api/database/stats")
        db_stats = response.json()
        print(f"DATABASE STATS: {db_stats}")
    except Exception as e:
        print(f"DATABASE STATS ERROR: {e}")
    
    print(f"\n🎯 TEST COMPLETED at: {datetime.now()}")
    print("=" * 80)

if __name__ == "__main__":
    main()