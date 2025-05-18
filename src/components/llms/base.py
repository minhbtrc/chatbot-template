"""
Base LLM client module.

This module defines the base interface for all LLM clients.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from injector import inject

from src.common.config import Config


class BaseLLMClient(ABC):
    """
    Base abstract class for all LLM clients.
    
    This defines a standard interface that all LLM client implementations
    must follow to ensure consistent usage across the application.
    """
    @inject
    def __init__(self, config: Config):
        self.config = config
        self.client: Any = None

    @abstractmethod
    def bind_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Bind tools to the LLM client.
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
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
    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send a completion prompt to the LLM and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model-specific parameters
            
        Returns:
            The LLM's completion as a string
        """
        pass
    
    async def achat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send a chat message to the LLM asynchronously and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model-specific parameters
            
        Returns:
            The LLM's response as a string
        """
        # Default implementation calls the synchronous method
        # Subclasses should override with true async implementation
        import asyncio
        return await asyncio.to_thread(self.chat, messages, **kwargs)
    
    async def acomplete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send a completion prompt to the LLM asynchronously and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model-specific parameters
            
        Returns:
            The LLM's completion as a string
        """
        # Default implementation calls the synchronous method
        # Subclasses should override with true async implementation
        import asyncio
        return await asyncio.to_thread(self.complete, prompt, **kwargs)
    
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