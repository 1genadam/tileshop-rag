#!/usr/bin/env python3
"""
Test script for installation query enhancement
"""

from modules.aos_chat_manager import AOSChatManager
from modules.db_manager import DatabaseManager

def test_installation_query_enhancement():
    """Test that installation queries with product names trigger purchase verification"""
    
    # Initialize managers
    db_manager = DatabaseManager()
    aos_chat = AOSChatManager(db_manager)
    
    print("=== Testing Installation Query Enhancement ===\n")
    
    # Test 1: Installation query with product name (should trigger purchase verification)
    print("Test 1: 'how do i install permat'")
    print("Expected: Should trigger purchase verification and request phone number")
    
    result = aos_chat.process_chat_with_purchase_verification("how do i install permat")
    print(f"Result: {result}")
    print(f"Needs phone number: {result.get('needs_phone_number')}")
    print(f"Phase: {result.get('phase')}")
    print(f"Response: {result.get('response')}")
    print()
    
    # Test 2: Installation query with phone number (should verify purchase)
    print("Test 2: 'how do i install permat' with phone number")
    print("Expected: Should verify purchase and provide installation guidance")
    
    result = aos_chat.process_chat_with_purchase_verification(
        "how do i install permat", 
        phone_number="847-302-2594"
    )
    print(f"Result: {result}")
    print(f"Purchase verified: {result.get('purchase_verified')}")
    print(f"Response: {result.get('response')}")
    print()
    
    # Test 3: General installation query (should NOT trigger purchase verification)
    print("Test 3: 'how do i install tile'")
    print("Expected: Should NOT trigger purchase verification")
    
    result = aos_chat.process_chat_with_purchase_verification("how do i install tile")
    print(f"Result: {result}")
    print(f"Needs phone number: {result.get('needs_phone_number')}")
    print(f"Phase: {result.get('phase')}")
    print()
    
    # Test 4: Explicit purchase mention (should trigger purchase verification)
    print("Test 4: 'i bought permat and need help'")
    print("Expected: Should trigger purchase verification")
    
    result = aos_chat.process_chat_with_purchase_verification("i bought permat and need help")
    print(f"Result: {result}")
    print(f"Needs phone number: {result.get('needs_phone_number')}")
    print(f"Phase: {result.get('phase')}")
    print()
    
    print("=== Testing Information Extraction ===\n")
    
    # Test the extract_information_from_query method directly
    test_queries = [
        "how do i install permat",
        "how do i install tile", 
        "i bought permat and need help",
        "installation instructions for backer-lite",
        "help with heat mat installation"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        extracted = aos_chat.extract_information_from_query(query)
        print(f"Extracted info: {extracted}")
        print(f"Mentions purchase: {extracted.get('mentions_purchase')}")
        print(f"Installation inquiry: {extracted.get('installation_inquiry')}")
        print(f"Mentioned product: {extracted.get('mentioned_product')}")
        print()

if __name__ == "__main__":
    test_installation_query_enhancement()