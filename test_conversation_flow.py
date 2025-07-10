#!/usr/bin/env python3
"""
Test script for improved conversation flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.aos_chat_manager import AOSChatManager
from modules.db_manager import DatabaseManager

def test_conversation_flow():
    """Test the improved conversation flow"""
    print("=== Testing Improved Conversation Flow ===\n")
    
    # Initialize managers
    db_manager = DatabaseManager()
    aos_chat = AOSChatManager(db_manager)
    
    # Test customer info
    phone_number = "847-302-2594"
    first_name = "Robert"
    
    # Test conversation sequence from user's example
    test_messages = [
        "looking for floor tile",
        "diy"
    ]
    
    print(f"Testing conversation flow for {first_name} ({phone_number})")
    print("-" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"User: {message}")
        
        # Process the message
        result = aos_chat.process_chat_message(message, phone_number, first_name)
        
        if result['success']:
            print(f"AI Response: {result['response'][:200]}...")
            print(f"Current Phase: {result['current_phase']}")
            print(f"Phase Changed: {result['phase_changed']}")
            print(f"Collected Info: {result['collected_info']}")
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 50)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_conversation_flow()