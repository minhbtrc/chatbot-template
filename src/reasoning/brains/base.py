"""
Base brain module that defines the interface for all brain implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


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
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the input query and return a response.
        
        Args:
            query: The user's input query
            context: Optional context information (conversation history, etc.)
            
        Returns:
            Response text
        """
        pass
    
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
