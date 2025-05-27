"""
Base brain module that defines the interface for all brain implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Generator, AsyncGenerator


class BaseBrain(ABC):
    """
    Abstract base class for all brain implementations.
    
    A brain is responsible for processing input and generating responses.
    It encapsulates the reasoning logic, which can be:
    - A direct call to an LLM
    - A chain of operations
    - An agent with tool-using capabilities
    """
    
    @abstractmethod
    def think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the input query and return a response.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing the response
        """
        pass

    @abstractmethod
    async def athink(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the input query and return a response asynchronously.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
            **kwargs: Additional arguments
            
        Returns:
            Dictionary containing the response
        """
        pass
    
    def stream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Generator[str, None, None]:
        """
        Process the input query and stream the response.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
            **kwargs: Additional arguments
            
        Yields:
            Chunks of the response content
        """
        # Default implementation: fall back to non-streaming
        response = self.think(history, system_message)
        yield response.get("content", "")
    
    async def astream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Process the input query and stream the response asynchronously.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
            **kwargs: Additional arguments
            
        Yields:
            Chunks of the response content
        """
        # Default implementation: fall back to non-streaming
        response = await self.athink(history, system_message, **kwargs)
        yield response.get("content", "")
    
    @abstractmethod
    def reset(self) -> None:
        """
        Reset the brain's state.
        
        This can include clearing cache, conversation history, etc.
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the brain.
        
        Returns:
            Dictionary with brain information
        """
        return {
            "type": self.__class__.__name__,
        }
    
    def use_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Configure the brain to use the provided tools.
        
        Args:
            tools: List of tools to use
        """
        # Default implementation does nothing
        pass
