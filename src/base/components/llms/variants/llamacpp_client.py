"""
LlamaCpp client module.

This module provides a client for interacting with LlamaCpp models.
"""

from typing import Dict, Any, Optional, List, Generator, AsyncGenerator

from injector import inject
from langchain_community.llms import LlamaCpp

from src.base.components.llms.base import BaseLLMClient
from src.common.config import Config
from src.common.logging import logger


class LlamaCppClient(BaseLLMClient):
    """Client for interacting with LlamaCpp models."""
    @inject
    def __init__(self, config: Config):
        """
        Initialize the LlamaCpp client.
        
        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.model_path = getattr(config, "model_path", None)
        self.client = self.create_llm()

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

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """Send a chat message using LlamaCpp."""
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        response = self.client.invoke(prompt, **kwargs)
        return {"content": response, "additional_kwargs": {}}

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Generator[str, None, None]:
        """Stream chat using LlamaCpp (fallback to non-streaming)."""
        response = self.chat(messages, **kwargs)
        yield response.get("content", "")

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        """Async stream chat using LlamaCpp (fallback)."""
        response = await self.achat(messages, **kwargs)
        yield response.get("content", "")

    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a completion prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def get_model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            "provider": "LlamaCpp",
            "model_path": self.model_path,
        }
    
    def close(self):
        """Close any open resources."""
        # No resources to explicitly close for LlamaCpp client
        pass 