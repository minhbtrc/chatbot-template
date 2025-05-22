"""
Custom in-memory implementation for chat history.
"""

from typing import Dict, List, Any

from src.base.components.memories.base import BaseChatbotMemory


class InMemory(BaseChatbotMemory):
    """
    Simple in-memory implementation of the chat history.
    
    This implementation stores all messages in memory.
    """
    
    def __init__(self):
        """Initialize the memory."""
        self.memory: Dict[str, List[Dict[str, Any]]] = {}
    
    def _add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
            conversation_id: ID of the conversation
        """
        if message["conversation_id"] not in self.memory:
            self.memory[message["conversation_id"]] = []
        
        self.memory[message["conversation_id"]].append(message)
    
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        return self.memory.get(conversation_id, [])
    
    def clear_history(self, conversation_id: str) -> None:
        """
        Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        if conversation_id in self.memory:
            self.memory[conversation_id] = []
    
    def get_all_conversations(self) -> List[str]:
        """
        Get all conversation IDs.
        
        Returns:
            List of conversation IDs
        """
        return list(self.memory.keys())

    def close(self) -> None:
        """Close the memory."""
        pass