"""
Base tool module.

This module defines the base interface for all tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class BaseTool(ABC):
    """
    Base abstract class for all tools.
    
    This defines a standard interface that all tool implementations
    must follow to ensure consistent usage across the application.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the tool.
        
        Args:
            name: Name of the tool
            description: Description of the tool's functionality
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        Execute the tool with the given input.
        
        Args:
            input_data: Input data for the tool
            
        Returns:
            Tool execution result
        """
        pass
    
    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Convert the tool to an OpenAI tool format.
        
        Returns:
            Tool definition in OpenAI format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            }
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for the tool's parameters.
        
        Returns:
            JSON schema defining the tool's parameters
        """
        pass


class SimpleTool(BaseTool):
    """
    A simple tool implementation that wraps a function.
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        func: Callable[[Any], Any],
        parameters_schema: Dict[str, Any]
    ):
        """
        Initialize the simple tool.
        
        Args:
            name: Name of the tool
            description: Description of the tool's functionality
            func: Function to execute
            parameters_schema: JSON schema for the function parameters
        """
        super().__init__(name, description)
        self.func = func
        self._parameters_schema = parameters_schema
    
    def run(self, input_data: Any) -> Any:
        """
        Execute the wrapped function with the given input.
        
        Args:
            input_data: Input data for the function
            
        Returns:
            Function execution result
        """
        return self.func(input_data)
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for the tool's parameters.
        
        Returns:
            JSON schema defining the tool's parameters
        """
        return self._parameters_schema 