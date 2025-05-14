"""
Azure OpenAI client module.

This module provides a client for interacting with Azure OpenAI models.
"""

from typing import Dict, Any, Optional, List, Union
import logging

from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI

from src.llms.base import BaseLLMClient
from infrastructure.config import Config

logger = logging.getLogger(__name__)


class AzureOpenAIClient(BaseLLMClient):
    """Client for interacting with Azure OpenAI models."""
    
    def __init__(self, config: Config):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Log configuration for debugging
        logger.debug(f"Azure OpenAI Configuration: endpoint={config.azure_endpoint}, "
                    f"deployment={config.azure_deployment_name}, api_version={config.azure_api_version}")
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                api_key=config.azure_api_key,
                api_version=config.azure_api_version,
                azure_endpoint=config.azure_endpoint or ""
            )
            self.deployment_name = config.azure_deployment_name
            self.temperature = getattr(config, "temperature", 0.7)
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Send a chat message to Azure OpenAI and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model parameters
            
        Returns:
            The model's response as a string
        """
        # Override default parameters with kwargs
        deployment = kwargs.get('deployment_name', self.deployment_name)
        temperature = kwargs.get('temperature', self.temperature)
        
        if not deployment:
            error_msg = "No deployment name specified for Azure OpenAI"
            logger.error(error_msg)
            return error_msg
        
        # Format messages for API
        formatted_messages: List[Dict[str, str]] = []
        for msg in messages:
            if 'role' in msg and 'content' in msg:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        logger.debug(f"Sending request to Azure OpenAI: deployment={deployment}, "
                    f"messages={formatted_messages}, temperature={temperature}")
        
        try:
            # Call the Azure OpenAI API
            # For Azure OpenAI, the deployment name is passed as the model parameter
            response = self.client.chat.completions.create(
                model=deployment,  # Use model instead of deployment_id
                messages=formatted_messages,
                temperature=temperature,
            )
            
            # Return the content of the first choice
            content = response.choices[0].message.content
            return content or ""  # Return empty string if content is None
        except Exception as e:
            error_msg = f"Error calling Azure OpenAI API: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Send a completion prompt to Azure OpenAI and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model parameters
            
        Returns:
            The model's completion as a string
        """
        # For Azure OpenAI, we'll use the chat completions API with a user message
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def create_embedding(self, text: Union[str, List[str]], **kwargs: Any) -> List[List[float]]:
        """
        Create embeddings for the given text(s).
        
        Args:
            text: Text or list of texts to create embeddings for
            **kwargs: Additional model parameters
            
        Returns:
            List of embedding vectors
        """
        # Prepare the input
        if isinstance(text, str):
            input_texts = [text]
        else:
            input_texts = text
        
        # Get deployment from kwargs or use default
        deployment = kwargs.get('deployment_name', self.config.azure_embedding_deployment_name)
        
        if not deployment:
            logger.error("No embedding deployment name specified for Azure OpenAI")
            return [[0.0]]  # Return a default embedding
        
        try:
            # Call the Azure OpenAI API with the correct parameters
            # For Azure OpenAI embeddings, the deployment name is passed as the model parameter
            response = self.client.embeddings.create(
                model=deployment,  # Use model instead of deployment_id
                input=input_texts
            )
            
            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            # Log the error and return empty embeddings
            logger.error(f"Error creating embeddings: {str(e)}")
            return [[0.0]]  # Return a default embedding
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the Azure OpenAI model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": "Azure OpenAI",
            "deployment": self.deployment_name,
            "temperature": self.temperature,
            "endpoint": self.config.azure_endpoint
        }
    
    def create_chat_model(self, model_kwargs: Optional[Dict[str, Any]] = None) -> AzureChatOpenAI:
        """
        Create a AzureChatOpenAI model instance from LangChain.
        
        Args:
            model_kwargs: Model parameters
            
        Returns:
            AzureChatOpenAI instance
        """
        kwargs = model_kwargs or {}
        
        # Set default parameters
        default_params = {
            "deployment_name": self.deployment_name,  # LangChain uses deployment_name
            "temperature": self.temperature,
            "openai_api_key": self.config.azure_api_key,
            "openai_api_version": self.config.azure_api_version,
            "azure_endpoint": self.config.azure_endpoint
        }
        
        # Override defaults with provided kwargs
        for key, value in default_params.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Create the model
        return AzureChatOpenAI(**kwargs)
    
    def close(self) -> None:
        """Close any open resources."""
        # No resources to close for Azure OpenAI client
        pass 