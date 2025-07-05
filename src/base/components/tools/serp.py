"""
Custom search tool module.

This module provides a tool for web search using the SerpAPI wrapper.

Visit https://serpapi.com/ to get your API key.
"""

import os
from typing import Optional, Dict, Any

from langchain_community.utilities import SerpAPIWrapper

from src.base.components.tools.base import BaseTool


class CustomSearchTool(BaseTool):
    """Tool for performing web searches via SerpAPI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the search tool.
        
        Args:
            api_key: Optional SerpAPI key (if not provided in environment)
        """
        super().__init__(
            name="web_search",
            description="Useful for when you need to answer questions about current events, date, or factual information"
        )
        serpapi_api_key=api_key or os.getenv("SERPAPI_API_KEY")
        if not serpapi_api_key:
            raise ValueError("SERPAPI_API_KEY is not set")
        
        self._search = SerpAPIWrapper(
            params={
                "engine": "google",
                "gl": "us",
                "hl": "en",
            },
            serpapi_api_key=serpapi_api_key
        )

    def run(self, input_data: str) -> str:
        """
        Execute the search with the given query.
        
        Args:
            input_data: The search query
            
        Returns:
            Search results as a string
        """
        return self._search.run(input_data)
    
    def search(self, input_data: str):
        return self._search.results(input_data)
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for the tool's parameters.
        
        Returns:
            JSON schema defining the tool's parameters
        """
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
