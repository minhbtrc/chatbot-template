"""
MongoDB memory implementation.
"""

from typing import Dict, List, Optional, Set
import datetime

from src.memory.base_memory import BaseChatbotMemory
from infrastructure.db.mongodb import MongoDBClient
from src.common.config import Config


class MongoMemory(BaseChatbotMemory):
    """
    MongoDB-based memory implementation.
    
    Stores conversation history in a MongoDB collection.
    """
    
    def __init__(self, config: Config, mongo_client: Optional[MongoDBClient] = None):
        """
        Initialize the MongoDB memory.
        
        Args:
            config: Application configuration
            mongo_client: MongoDB client (created if not provided)
        """
        self.config = config
        self.client = mongo_client or MongoDBClient(config)
        self.conversation_cache: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, role: str, content: str, conversation_id: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
            conversation_id: ID of the conversation
        """
        # Create the message document
        message = {
            "role": role,
            "content": content,
            "conversation_id": conversation_id,
            "timestamp": datetime.datetime.now()
        }
        
        # Insert the message into the database
        self.client.insert_one(message)
        
        # Clear the cache for this conversation
        if conversation_id in self.conversation_cache:
            del self.conversation_cache[conversation_id]
    
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        # Check if we have a cached version
        if conversation_id in self.conversation_cache:
            return self.conversation_cache[conversation_id]
        
        # Query the database for messages in this conversation
        messages = self.client.find_many({
            "conversation_id": conversation_id
        })
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", 0))
        
        # Format for the brain (only include role and content)
        formatted_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
            if "role" in msg and "content" in msg
        ]
        
        # Cache the result
        self.conversation_cache[conversation_id] = formatted_messages
        
        return formatted_messages
    
    def clear_history(self, conversation_id: str) -> None:
        """
        Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        # Delete all messages in this conversation
        query = {"conversation_id": conversation_id}
        
        # MongoDB doesn't have a delete_many method in our interface, so we use a loop
        messages = self.client.find_many(query)
        for msg in messages:
            if "_id" in msg:
                self.client.delete_one({"_id": msg["_id"]})
        
        # Clear the cache for this conversation
        if conversation_id in self.conversation_cache:
            del self.conversation_cache[conversation_id]
    
    def get_all_conversations(self) -> List[str]:
        """
        Get all conversation IDs.
        
        Returns:
            List of conversation IDs
        """
        # Find all unique conversation IDs
        messages = self.client.find_many({})
        conversation_ids: Set[str] = set()
        
        for msg in messages:
            if "conversation_id" in msg:
                conversation_ids.add(msg["conversation_id"])
        
        return list(conversation_ids) 