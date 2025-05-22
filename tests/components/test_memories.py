import unittest
from typing import Dict, List

from src.common.config import Config
from src.base.components.memories import create_memory, InMemory, MongoMemory


class TestMemories(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_config = Config()
        self.mock_config.bot_memory_type = "inmemory"
        self.mock_mongo_config = Config()
        self.mock_mongo_config.bot_memory_type = "mongodb"
        self.mock_mongo_config.mongo_uri = "mongodb://localhost:27017"
        self.mock_mongo_config.mongo_database = "test_db"
        self.mock_mongo_config.mongo_collection = "test_collection"

    def test_create_valid_memory(self) -> None:
        memory = create_memory(self.mock_config)
        assert isinstance(memory, InMemory)

        mongo_memory = create_memory(self.mock_mongo_config)
        assert isinstance(mongo_memory, MongoMemory)

    def test_create_memory_invalid_type(self) -> None:
        config = Config()
        config.bot_memory_type = "invalid"
        with self.assertRaises(ValueError):
            create_memory(config)

    def test_add_message_return_type(self) -> None:
        memory = create_memory(self.mock_config)
        
        # Test add_message (should return None)
        result = memory.add_message("user", "test message", "test_conversation")
        assert result is None

    def test_get_history_return_type(self) -> None:
        memory = create_memory(self.mock_config)
        
        # Add some messages first
        memory.add_message("user", "test message 1", "test_conversation")
        memory.add_message("assistant", "test response 1", "test_conversation")
        
        # Test get_history
        result = memory.get_history("test_conversation")
        assert isinstance(result, List)
        assert all(isinstance(msg, Dict) for msg in result)
        assert all("role" in msg and "content" in msg for msg in result)

    def test_clear_history_return_type(self) -> None:
        memory = create_memory(self.mock_config)
        
        # Add a message first
        memory.add_message("user", "test message", "test_conversation")
        
        # Test clear_history (should return None)
        result = memory.clear_history("test_conversation")
        assert result is None

    def test_get_all_conversations_return_type(self) -> None:
        memory = create_memory(self.mock_config)
        
        # Add messages to multiple conversations
        memory.add_message("user", "test message 1", "conversation_1")
        memory.add_message("user", "test message 2", "conversation_2")
        
        # Test get_all_conversations
        result = memory.get_all_conversations()
        assert isinstance(result, List)
        assert all(isinstance(conv_id, str) for conv_id in result)

    def test_close_return_type(self) -> None:
        memory = create_memory(self.mock_config)
        
        # Test close (should return None)
        result = memory.close()
        assert result is None
