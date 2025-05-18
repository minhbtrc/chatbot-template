"""
Tools module for the chatbot application.

This module provides tools and utilities for the bot to use for various tasks.
"""

from typing import List, Any

from langchain_core.tools import Tool

from .serp import CustomSearchTool
from .base import BaseTool, SimpleTool


class ToolProvider:
    """
    Manages and provides access to available tools for the bot.
    
    This class centralizes tool management, making it easier to add, remove, 
    or configure tools across the application.
    """
    
    def __init__(self):
        """Initialize the tool provider with default tools."""
        self._tools: List[Any] = []
        
        # Register default tools here
        self.register_tool(CustomSearchTool())
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a new tool.
        
        Args:
            tool: The tool to register
        """
        self._tools.append(tool)
    
    def get_tools(self) -> List[Any]:
        """
        Get all registered tools.
        
        Returns:
            List of registered tools
        """
        return self._tools
    
    def get_langchain_tools(self) -> List[Tool]:
        """
        Get all registered tools as LangChain tools.
        
        Returns:
            List of registered tools as LangChain tools
        """
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                func=tool.run,
                verbose=True
            )
            for tool in self._tools
        ]

# Export public classes and functions
__all__ = ["CustomSearchTool", "BaseTool", "SimpleTool", "ToolProvider"]
