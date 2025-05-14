"""
Base LLM client module.

This module defines the base interface for all LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class BaseLLMClient(ABC):
    """
    Base abstract class for all LLM clients.
    
    This defines a standard interface that all LLM client implementations
    must follow to ensure consistent usage across the application.
    """
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Send a chat message to the LLM and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model-specific parameters
            
        Returns:
            The LLM's response as a string
        """
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Send a completion prompt to the LLM and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model-specific parameters
            
        Returns:
            The LLM's completion as a string
        """
        pass
    
    @abstractmethod
    def create_embedding(self, text: Union[str, List[str]], **kwargs: Any) -> List[List[float]]:
        """
        Create embeddings for the given text(s).
        
        Args:
            text: Text or list of texts to create embeddings for
            **kwargs: Additional model-specific parameters
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model.
        
        Returns:
            Dictionary with model information
        """
        pass
    
    def close(self) -> None:
        """
        Close any resources used by the client.
        
        This method should be called when the client is no longer needed.
        Default implementation does nothing.
        """
        pass 