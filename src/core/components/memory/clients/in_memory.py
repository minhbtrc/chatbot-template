"""
Custom in-memory implementation for chat history.
"""

from typing import Dict, List

from src.core.components.memory.base import BaseChatbotMemory


class InMemory(BaseChatbotMemory):
    """
    Simple in-memory implementation of the chat history.
    
    This implementation stores all messages in memory.
    """
    
    def __init__(self):
        """Initialize the memory."""
        self.memory: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, role: str, content: str, conversation_id: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
            conversation_id: ID of the conversation
        """
        if conversation_id not in self.memory:
            self.memory[conversation_id] = []
        
        self.memory[conversation_id].append({"role": role, "content": content})
    
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