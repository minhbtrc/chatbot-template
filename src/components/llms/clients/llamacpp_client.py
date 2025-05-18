"""
LlamaCpp client module.

This module provides a client for interacting with LlamaCpp models.
"""

from typing import Dict, Any, Optional, List

from injector import inject
from langchain_community.llms import LlamaCpp

from src.common.config import Config
from src.common.logging import logger

class LlamaCppClient:
    """Client for interacting with LlamaCpp models."""
    @inject
    def __init__(self, config: Config):
        """
        Initialize the LlamaCpp client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model_path = getattr(config, "model_path", None)

    def bind_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Bind tools to the LlamaCpp client.
        """
        logger.warning("LlamaCpp client doesn't support tools")
    
    def create_llm(self, model_kwargs: Optional[Dict[str, Any]] = None) -> LlamaCpp:
        """
        Create a LlamaCpp model instance.
        
        Args:
            model_kwargs: Model parameters
            
        Returns:
            LlamaCpp instance
        """
        kwargs = model_kwargs or {}
        
        # Handle model_path
        if "model_path" not in kwargs:
            if self.model_path:
                kwargs["model_path"] = self.model_path
            else:
                raise ValueError("No model_path provided in config or parameters")
        
        # Set default parameters
        default_params = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "n_ctx": 2048,
        }
        
        # Override defaults with provided kwargs
        for key, value in default_params.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Create the model
        return LlamaCpp(**kwargs)
    
    def close(self):
        """Close any open resources."""
        # No resources to explicitly close for LlamaCpp client
        pass 