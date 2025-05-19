"""
Azure OpenAI client module.

This module provides a client for interacting with Azure OpenAI models.
"""

from typing import Dict, Any, Optional, List
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import SecretStr

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from openai import APIError as OpenAIAPIError
from openai import RateLimitError as OpenAIRateLimitError
from openai import APIConnectionError as OpenAIConnectionError
from injector import inject

from src.core.components.llms.base import BaseLLMClient
from src.common.config import Config
from src.common.exceptions import APIError, RateLimitError, ConnectionError, LLMClientError
from src.common.logging import logger


class AzureOpenAIClient(BaseLLMClient):
    """Client for interacting with Azure OpenAI models."""
    @inject
    def __init__(self, config: Config):
        """
        Initialize the Azure OpenAI client.
        
        Args:
            config: Application configuration
            
        Raises:
            ConnectionError: If the client fails to initialize
        """
        try:
            self.config = config
            
            # Log configuration for debugging
            logger.info(f"Azure OpenAI Configuration: endpoint={config.azure_chat_model_endpoint}, "
                        f"deployment={config.azure_chat_model_deployment}, api_version={config.azure_chat_model_version}")
            
            # Initialize Azure OpenAI client
            self.temperature = getattr(config, "temperature", 0.7)
            self.max_retries = getattr(config, "max_retries", 3)
            self.request_timeout = getattr(config, "request_timeout", 60)

            callbacks: List[Any] = []
            if config.enable_langfuse:
                from langfuse.callback import CallbackHandler
                langfuse_handler = CallbackHandler(
                    secret_key=config.langfuse_secret_key,
                    public_key=config.langfuse_public_key,
                    host=config.langfuse_host
                )
                callbacks = [langfuse_handler]

            self.client = AzureChatOpenAI(
                azure_deployment=config.azure_chat_model_deployment,
                api_key=SecretStr(config.azure_chat_model_key or ""),
                api_version=config.azure_chat_model_version,
                azure_endpoint=config.azure_chat_model_endpoint or "",
                temperature=self.temperature,
                max_retries=self.max_retries,
                timeout=self.request_timeout,
                callbacks=callbacks
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise ConnectionError(f"Failed to initialize Azure OpenAI client: {str(e)}")
    
    def bind_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Bind tools to the Azure OpenAI client.
        """
        if tools:
            self.client = self.client.bind_tools([tool.to_openai_tool() for tool in tools])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((OpenAIConnectionError, OpenAIRateLimitError)),
        reraise=True
    )
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send a chat message to Azure OpenAI and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model parameters
            
        Returns:
            The model's response as a string
            
        Raises:
            APIError: If the API call fails
            RateLimitError: If rate limits are exceeded
            ConnectionError: If connection to Azure OpenAI fails
            LLMClientError: For any other errors
        """
        try:
            # Format messages for API - convert to the expected OpenAI format
            formatted_messages: List[BaseMessage] = []
            for msg in messages:
                if 'role' in msg and 'content' in msg:
                    role = msg["role"]
                    content = msg["content"]
                    
                    # Create proper ChatCompletionMessageParam objects based on role
                    if role == "user":
                        formatted_messages.append(HumanMessage(content))
                    elif role == "assistant":
                        formatted_messages.append(AIMessage(content))
                    elif role == "system":
                        formatted_messages.append(SystemMessage(content))
            # Call the Azure OpenAI API
            # For Azure OpenAI, the deployment name is passed as the model parameter
            response = self.client.invoke(
                input=formatted_messages
            )
            
            # Return the content of the first choice
            return {"content": response.content, "additional_kwargs": response.additional_kwargs}  # Return empty string if content is None
            
        except OpenAIRateLimitError as e:
            logger.warning(f"Azure OpenAI rate limit exceeded: {str(e)}")
            # Handle retry_after which might be None
            retry_after = getattr(e, "retry_after", None)
            retry_after_int = int(retry_after) if retry_after is not None else None
            raise RateLimitError(f"Azure OpenAI rate limit exceeded: {str(e)}", retry_after=retry_after_int)
        except OpenAIConnectionError as e:
            logger.error(f"Connection to Azure OpenAI failed: {str(e)}")
            raise ConnectionError(f"Connection to Azure OpenAI failed: {str(e)}")
        except OpenAIAPIError as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            # Handle status_code which might be None
            status_code = getattr(e, "status_code", None)
            status_code_int = int(status_code) if status_code is not None else None
            raise APIError(f"Azure OpenAI API error: {str(e)}", status_code=status_code_int)
        except Exception as e:
            logger.error(f"Unexpected error in Azure OpenAI client: {str(e)}")
            raise LLMClientError(f"Unexpected error in Azure OpenAI client: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((OpenAIConnectionError, OpenAIRateLimitError)),
        reraise=True
    )
    def complete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send a completion prompt to Azure OpenAI and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model parameters
            
        Returns:
            The model's completion as a string
            
        Raises:
            APIError: If the API call fails
            RateLimitError: If rate limits are exceeded
            ConnectionError: If connection to Azure OpenAI fails
            LLMClientError: For any other errors
        """
        # For Azure OpenAI, we'll use the chat completions API with a user message
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    async def achat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send a chat message to Azure OpenAI asynchronously and get a response.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional model parameters
            
        Returns:
            The model's response as a string
            
        Raises:
            APIError: If the API call fails
            RateLimitError: If rate limits are exceeded
            ConnectionError: If connection to Azure OpenAI fails
            LLMClientError: For any other errors
        """
        # For simplicity, we'll use the sync client in an executor
        # In a production environment, you would use a dedicated async client
        return await asyncio.to_thread(self.chat, messages, **kwargs)
    
    async def acomplete(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Send a completion prompt to Azure OpenAI asynchronously and get a response.
        
        Args:
            prompt: The text prompt to complete
            **kwargs: Additional model parameters
            
        Returns:
            The model's completion as a string
            
        Raises:
            APIError: If the API call fails
            RateLimitError: If rate limits are exceeded
            ConnectionError: If connection to Azure OpenAI fails
            LLMClientError: For any other errors
        """
        # Use achat with a single user message
        messages = [{"role": "user", "content": prompt}]
        return await self.achat(messages, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the Azure OpenAI model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": "Azure OpenAI",
            "deployment": self.config.azure_chat_model_deployment,
            "temperature": self.temperature,
            "endpoint": self.config.azure_chat_model_endpoint,
            "max_retries": self.max_retries,
            "request_timeout": self.request_timeout
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
            "deployment_name": self.config.azure_chat_model_deployment,  # LangChain uses deployment_name
            "temperature": self.temperature,
            "openai_api_key": self.config.azure_chat_model_key,
            "openai_api_version": self.config.azure_chat_model_version,
            "azure_endpoint": self.config.azure_chat_model_endpoint,
            "request_timeout": self.request_timeout
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