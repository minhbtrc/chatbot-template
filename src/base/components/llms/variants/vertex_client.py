"""
Vertex AI client wrapper for integration with LangChain.
"""

from typing import Dict, Any, Optional, List, Generator, AsyncGenerator
import os
import json

from injector import inject
from langchain_google_vertexai import ChatVertexAI
import vertexai

from src.base.components.llms.base import BaseLLMClient
from src.common.config import Config
from src.common.logging import logger


class VertexAIClient(BaseLLMClient):
    """Wrapper for Vertex AI API integration."""
    @inject
    def __init__(self, config: Config):
        """
        Initialize the Vertex AI client.
        
        Args:
            config: Application configuration
        """
        super().__init__(config)
        self.credentials_file = os.getenv("CREDENTIALS_FILE") or getattr(config, "credentials", None)
        
        if not self.credentials_file:
            raise ValueError("Vertex AI credentials file not found in environment or config")
        
        self._initialize_vertex_ai()
        self.client = self.create_chat_model()

    def bind_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Bind tools to the Vertex AI client.
        """
        logger.warning("Vertex AI client doesn't support tools")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with credentials."""
        try:
            with open(self.credentials_file, "r") as f:
                credential_data = json.load(f)
            
            project_id = credential_data.get("project_id")
            
            if not project_id:
                raise ValueError("Project ID not found in credentials file")
            
            # Set environment variables
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_file
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            
            # Initialize Vertex AI
            vertexai.init(project=project_id, location="us-central1")
        except Exception as e:
            raise ValueError(f"Failed to initialize Vertex AI: {str(e)}")
    
    def create_chat_model(self, model_kwargs: Optional[Dict[str, Any]] = None) -> ChatVertexAI:
        """
        Create a ChatVertexAI model instance.
        
        Args:
            model_kwargs: Optional model parameters
            
        Returns:
            ChatVertexAI instance
        """
        # Default model parameters
        default_kwargs = {
            "model_name": "gemini-1.5-pro",
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }
        
        # Merge default and provided parameters
        kwargs = {**default_kwargs, **(model_kwargs or {})}
        
        # Create and return the model
        return ChatVertexAI(**kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """Send a chat request to Vertex AI."""
        formatted_messages = [m["content"] for m in messages if "content" in m]
        prompt = "\n".join(formatted_messages)
        response = self.client.invoke(prompt, **kwargs)
        return {"content": response, "additional_kwargs": {}}

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Generator[str, None, None]:
        """Stream chat from Vertex AI. Fallback to non-streaming."""
        if hasattr(self.client, "stream"):
            formatted_messages = [m["content"] for m in messages if "content" in m]
            prompt = "\n".join(formatted_messages)
            for chunk in self.client.stream(prompt, **kwargs):
                yield chunk
        else:
            response = self.chat(messages, **kwargs)
            yield response.get("content", "")

    async def astream_chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> AsyncGenerator[str, None]:
        """Async stream chat from Vertex AI. Fallback to non-streaming."""
        if hasattr(self.client, "astream"):
            formatted_messages = [m["content"] for m in messages if "content" in m]
            prompt = "\n".join(formatted_messages)
            async for chunk in self.client.astream(prompt, **kwargs):
                yield chunk
        else:
            response = await self.achat(messages, **kwargs)
            yield response.get("content", "")

    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a completion prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def get_model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            "provider": "VertexAI",
            "credentials_file": self.credentials_file,
        }

    def close(self) -> None:
        """Close any resources used by the client."""
        pass
