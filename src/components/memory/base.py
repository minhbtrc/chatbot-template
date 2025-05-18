"""
Base memory interface for storing conversation history.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseChatbotMemory(ABC):
    """
    Abstract base class for all memory implementations.
    
    Memory is responsible for storing and retrieving conversation history.
    Different implementations can use different storage backends (e.g., in-memory, MongoDB, etc.).
    """
    
    @abstractmethod
    def add_message(self, role: str, content: str, conversation_id: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
            conversation_id: ID of the conversation
        """
        pass

    def add_messages(self, messages: List[Dict[str, str]], conversation_id: str) -> None:
        """
        Add a list of messages to the conversation history.
        
        Args:
            messages: List of messages to add
            conversation_id: ID of the conversation
        """
        for message in messages:
            self.add_message(role=message["role"], content=message["content"], conversation_id=conversation_id)
    
    @abstractmethod
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        pass
    
    @abstractmethod
    def clear_history(self, conversation_id: str) -> None:
        """
        Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        pass
    
    @abstractmethod
    def get_all_conversations(self) -> List[str]:
        """
        Get all conversation IDs.
        
        Returns:
            List of conversation IDs
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the memory.
        """
        pass
