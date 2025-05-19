"""
OpenAI client module.

This module provides a client for interacting with OpenAI models.
"""

from typing import Dict, Any, Optional, List

from injector import inject
from langchain_openai import ChatOpenAI
from openai import OpenAI

from src.core.components.llms.base import BaseLLMClient
from src.common.config import Config
from src.common.logging import logger


class OpenAIClient(BaseLLMClient):
    """Client for interacting with OpenAI models."""
    @inject
    def __init__(self, config: Config):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model_name = config.base_model_name or "gpt-3.5-turbo"
        self.temperature = 0.7

    def bind_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Bind tools to the OpenAI client.
        """
        logger.warning("OpenAI client doesn't support tools")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send a chat message to OpenAI and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model parameters
            
        Returns:
            The model's response as a string
        """
        # Override default parameters with kwargs
        model_value = kwargs.get('model', self.model_name)
        model = str(model_value) if model_value is not None else self.model_name
        
        temp_value = kwargs.get('temperature', self.temperature)
        temperature = float(temp_value) if temp_value is not None else self.temperature
        
        # Convert messages to the format expected by OpenAI
        formatted_messages: List[Dict[str, str]] = []
        for msg in messages:
            # Ensure each message has 'role' and 'content' keys
            if 'role' in msg and 'content' in msg:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
        )
        
        # Return the content of the first choice
        content = response.choices[0].message.content
        return {"content": content, "additional_kwargs": getattr(response.choices[0].message, "additional_kwargs")}  # Return empty string if content is None
    
    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send a completion prompt to OpenAI and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model parameters
            
        Returns:
            The model's completion as a string
        """
        # For OpenAI, we'll use the chat completions API with a user message
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenAI model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": "OpenAI",
            "model": self.model_name,
            "temperature": self.temperature,
        }
    
    def create_chat_model(self, model_kwargs: Optional[Dict[str, Any]] = None) -> ChatOpenAI:
        """
        Create a ChatOpenAI model instance from LangChain.
        
        Args:
            model_kwargs: Model parameters
            
        Returns:
            ChatOpenAI instance
        """
        kwargs = model_kwargs or {}
        
        # Set default parameters
        default_params = {
            "model_name": self.model_name,
            "temperature": self.temperature,
        }
        
        # Override defaults with provided kwargs
        for key, value in default_params.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Create the model
        return ChatOpenAI(**kwargs)
    
    def close(self) -> None:
        """Close any open resources."""
        # No resources to close for OpenAI client
        pass 