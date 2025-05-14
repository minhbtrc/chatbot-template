"""
Brain factory module.

This module provides factory functions to create different brain implementations.
"""

from typing import Dict, Any, Optional

from src.reasoning.brains.base import BaseBrain
from src.reasoning.brains.openai_brain import OpenAIBrain
from src.reasoning.brains.llama_brain import LlamaBrain
from src.reasoning.brains.azure_openai_brain import AzureOpenAIBrain
from src.llms.clients.openai_client import OpenAIClient
from src.llms.clients.azure_openai_client import AzureOpenAIClient
from src.reasoning.chain_manager import ChainManager
from infrastructure.config import Config
from infrastructure.logging import logger


def create_brain(
    config: Config, 
    brain_type: Optional[str] = None, 
    chain_manager: Optional[ChainManager] = None,
    **kwargs: Any
) -> BaseBrain:
    """
    Create a brain based on the configuration or specified type.
    
    Args:
        config: Application configuration
        brain_type: Optional brain type override
        chain_manager: Optional chain manager for structured reasoning
        **kwargs: Additional parameters to pass to the brain constructor
        
    Returns:
        A brain instance
    """
    # Determine brain type from config or parameter
    brain_type = brain_type or getattr(config, "model_type", "openai").lower()
    
    # Log brain creation
    logger.info(f"Creating brain of type: {brain_type}")
    
    # Create the appropriate brain
    if brain_type == "llama":
        return create_llama_brain(config, chain_manager=chain_manager, **kwargs)
    elif brain_type == "azureopenai":
        return create_azure_openai_brain(config, chain_manager=chain_manager, **kwargs)
    else:
        # Default to OpenAI
        return create_openai_brain(config, chain_manager=chain_manager, **kwargs)


def create_azure_openai_brain(
    config: Config,
    model_kwargs: Optional[Dict[str, Any]] = None,
    chain_manager: Optional[ChainManager] = None,
    **kwargs: Any
) -> BaseBrain:
    """
    Create an Azure OpenAI brain.
    
    Args:
        config: Application configuration
        model_kwargs: Optional model parameters
        chain_manager: Optional chain manager for structured reasoning
        **kwargs: Additional parameters
        
    Returns:
        Azure OpenAI brain instance
    """
    # Create the Azure OpenAI client
    llm_client = kwargs.pop("llm_client", None) or AzureOpenAIClient(config)
    
    # Prepare model parameters
    model_kwargs = model_kwargs or {}
    
    # Create default parameters if not provided
    if not model_kwargs:
        model_kwargs = {
            "deployment_name": getattr(config, "azure_deployment_name", None),
            "temperature": getattr(config, "temperature", 0.7),
        }
    
    # Create and return the brain
    return AzureOpenAIBrain(
        config=config,
        llm_client=llm_client,
        model_kwargs=model_kwargs,
        chain_manager=chain_manager,
        **kwargs
    )


def create_openai_brain(
    config: Config, 
    model_kwargs: Optional[Dict[str, Any]] = None,
    chain_manager: Optional[ChainManager] = None,
    **kwargs: Any
) -> BaseBrain:
    """
    Create an OpenAI brain.
    
    Args:
        config: Application configuration
        model_kwargs: Optional model parameters
        chain_manager: Optional chain manager for structured reasoning
        **kwargs: Additional parameters
        
    Returns:
        OpenAIBrain instance
    """
    # Create the OpenAI client
    llm_client = kwargs.pop("llm_client", None) or OpenAIClient(config)
    
    # Prepare model parameters
    model_kwargs = model_kwargs or {}
    
    # Create default parameters if not provided
    if not model_kwargs:
        model_kwargs = {
            "model": getattr(config, "openai_model_name", "gpt-3.5-turbo"),
            "temperature": getattr(config, "temperature", 0.7),
        }
    
    # Create and return the brain
    return OpenAIBrain(
        config=config,
        llm_client=llm_client,
        model_kwargs=model_kwargs,
        chain_manager=chain_manager,
        **kwargs
    )


def create_llama_brain(
    config: Config, 
    model_kwargs: Optional[Dict[str, Any]] = None,
    chain_manager: Optional[ChainManager] = None,
    **kwargs: Any
) -> BaseBrain:
    """
    Create a Llama brain.
    
    Args:
        config: Application configuration
        model_kwargs: Optional model parameters
        chain_manager: Optional chain manager for structured reasoning
        **kwargs: Additional parameters
        
    Returns:
        LlamaBrain instance
    """
    # Import here to avoid requiring llama.cpp for non-llama users
    try:
        from src.llms.clients.llamacpp_client import LlamaCppClient
    except ImportError:
        raise ImportError(
            "Could not import LlamaClient. Please make sure llama.cpp is installed."
        )
    
    # Create the Llama client
    llm_client = kwargs.pop("llm_client", None) or LlamaCppClient(config)
    
    # Prepare model parameters
    model_kwargs = model_kwargs or {}
    
    # Create default parameters if not provided
    if not model_kwargs:
        model_kwargs = {
            "model_path": getattr(config, "llama_model_path", None),
            "temperature": getattr(config, "temperature", 0.7),
            "max_tokens": getattr(config, "max_tokens", 512),
        }
    
    # Create and return the brain
    return LlamaBrain(
        config=config,
        llm_client=llm_client,
        model_kwargs=model_kwargs,
        **kwargs
    )


def create_vertex_brain(
    config: Config,
    model_kwargs: Optional[Dict[str, Any]] = None,
    chain_manager: Optional[ChainManager] = None,
    **kwargs
) -> BaseBrain:
    """
    Create a Vertex AI brain.
    
    Not fully implemented yet - currently falls back to OpenAI.
    
    Args:
        config: Application configuration
        model_kwargs: Model parameters
        chain_manager: Optional chain manager for structured reasoning
        **kwargs: Additional parameters
        
    Returns:
        Vertex AI brain instance (falls back to OpenAI for now)
    """
    # TODO: Implement Vertex AI brain
    return OpenAIBrain(
        config=config,
        model_kwargs=model_kwargs,
        chain_manager=chain_manager,
        **kwargs
    ) 