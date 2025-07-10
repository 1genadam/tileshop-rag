#!/usr/bin/env python3
"""
Test script for purchase verification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.aos_chat_manager import AOSChatManager
from modules.db_manager import DatabaseManager

def test_purchase_verification():
    """Test the purchase verification system"""
    print("=== Testing Purchase Verification System ===\n")
    
    # Initialize managers
    db_manager = DatabaseManager()
    aos_chat = AOSChatManager(db_manager)
    
    # Test customer info
    phone_number = "847-302-2594"
    first_name = "Robert"
    
    print("=== Test 1: Customer mentions purchase without providing phone number ===")
    query1 = "i just bought permat from you guys and need to know how to install it"
    result1 = aos_chat.process_chat_with_purchase_verification(query1)
    
    print(f"Query: {query1}")
    print(f"Response: {result1['response']}")
    print(f"Needs Phone Number: {result1.get('needs_phone_number', False)}")
    print(f"Phase: {result1.get('phase', 'unknown')}")
    print("-" * 60)
    
    print("\n=== Test 2: Setting up sample customer data ===")
    # Create customer and add sample purchase data
    customer = db_manager.get_or_create_customer(phone_number, first_name)
    if customer:
        db_manager.add_sample_purchase_data(customer['customer_id'])
        print(f"✅ Created customer and sample purchase data for {first_name} ({phone_number})")
    print("-" * 60)
    
    print("\n=== Test 3: Customer mentions exact product they bought ===")
    query2 = "i bought backer-lite from you and need installation help"
    result2 = aos_chat.process_chat_with_purchase_verification(query2, phone_number, first_name)
    
    print(f"Query: {query2}")
    print(f"Response: {result2['response']}")
    print(f"Purchase Verified: {result2.get('purchase_verified', False)}")
    print(f"Phase: {result2.get('phase', 'unknown')}")
    print("-" * 60)
    
    print("\n=== Test 4: Customer mentions similar product (permat instead of backer-lite) ===")
    query3 = "i bought permat from you guys and need to know how to install it"
    result3 = aos_chat.process_chat_with_purchase_verification(query3, phone_number, first_name)
    
    print(f"Query: {query3}")
    print(f"Response: {result3['response']}")
    print(f"Purchase Verified: {result3.get('purchase_verified', False)}")
    print(f"Phase: {result3.get('phase', 'unknown')}")
    
    if result3.get('verification_result'):
        print(f"Verification Details:")
        verification = result3['verification_result']
        if verification.get('customer_has_related'):
            for related in verification['customer_has_related']:
                print(f"  - Customer actually bought: {related['purchased_product']['product_name']}")
                print(f"  - Related to mentioned: {related['related_to']}")
                print(f"  - Category: {related['category']}")
    print("-" * 60)
    
    print("\n=== Test 5: Customer mentions product they didn't buy ===")
    query4 = "i bought marble tile from you guys and need help"
    result4 = aos_chat.process_chat_with_purchase_verification(query4, phone_number, first_name)
    
    print(f"Query: {query4}")
    print(f"Response: {result4['response']}")
    print(f"Purchase Verified: {result4.get('purchase_verified', False)}")
    print(f"Phase: {result4.get('phase', 'unknown')}")
    print("-" * 60)
    
    print("\n=== Purchase Verification Test Complete ===")

if __name__ == "__main__":
    test_purchase_verification()