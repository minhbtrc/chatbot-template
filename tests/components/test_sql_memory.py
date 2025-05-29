#!/usr/bin/env python3
"""
Test script for SQL memory variants.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from src.database import initialize_database
from src.base.components.memories.variants.sql_memory import SQLMemory
from src.common.logging import logger


def test_sql_memory():
    """Test the synchronous SQL memory implementation."""
    print("\n=== Testing SQL Memory ===")
    
    # Initialize database
    initialize_database("sqlite:///test_memory.db")
    
    # Create memory instance
    memory = SQLMemory(user_id=1)
    
    conversation_id = "user_1_conv_test_sync"
    
    try:
        # Clear any existing history
        memory.clear_history(conversation_id)
        
        # Test adding messages
        print("Adding messages...")
        memory.add_message(
            role="user",
            content="Hello, this is a test message",
            conversation_id=conversation_id
        )
        
        memory.add_message(
            role="assistant",
            content="Hello! I received your test message.",
            conversation_id=conversation_id
        )
        
        # Test getting history
        print("Getting conversation history...")
        history = memory.get_history(conversation_id)
        print(f"Retrieved {len(history)} messages:")
        for i, msg in enumerate(history):
            print(f"  {i+1}. {msg['role']}: {msg['content']}")
        
        # Test getting all conversations
        print("Getting all conversations...")
        conversations = memory.get_all_conversations()
        print(f"Found {len(conversations)} conversations: {conversations}")
        
        # Test getting user conversations
        print("Getting user conversations...")
        user_conversations = memory.get_user_conversations(1)
        print(f"Found {len(user_conversations)} conversations for user 1: {user_conversations}")
        
        # Test clearing history
        print("Clearing conversation history...")
        memory.clear_history(conversation_id)
        
        # Verify history is cleared
        history_after_clear = memory.get_history(conversation_id)
        print(f"Messages after clear: {len(history_after_clear)}")
        
        print("✅ SQL Memory test completed successfully!")
        
    except Exception as e:
        print(f"❌ SQL Memory test failed: {str(e)}")
        logger.error(f"SQL Memory test error: {str(e)}")
    finally:
        memory.close()


def main():
    """Run all tests."""
    print("Starting SQL Memory Tests...")
    
    # Test synchronous SQL memory
    test_sql_memory()
    
    print("\nAll SQL Memory tests completed!")


if __name__ == "__main__":
    main() 