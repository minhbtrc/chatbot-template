"""
Dependency injection container for the application.

This module provides a centralized container for dependency injection,
making it easier to manage dependencies throughout the application.
"""

from typing import List, Optional

from dependency_injector import containers, providers

from src.bot.bot import Bot
from src.reasoning.brains.base import BaseBrain
from src.reasoning.brains.brain_factory import create_brain
from src.reasoning.chain_manager import ChainManager
from src.memory.base_memory import BaseChatbotMemory
from src.memory.custom_memory import CustomMemory
from src.memory.mongodb_memory import MongoMemory
from src.llms.clients.openai_client import OpenAIClient
from src.llms.clients.llamacpp_client import LlamaCppClient
from src.tools.base import BaseTool
from src.tools.serp import CustomSearchTool
from infrastructure.config import Config
from infrastructure.logging import logger


class Container(containers.DeclarativeContainer):
    """
    Dependency injection container for the application.
    
    This container manages the creation and lifecycle of all application
    components, ensuring proper dependency injection.
    """
    
    # Configuration
    config = providers.Singleton(Config)
    
    # Tools
    search_tool = providers.Singleton(CustomSearchTool)
    
    # LLM clients
    openai_client = providers.Singleton(OpenAIClient, config=config)
    llama_client = providers.Singleton(LlamaCppClient, config=config)
    
    # Chain manager
    chain_manager = providers.Factory(
        ChainManager,
        llm_client=openai_client
    )
    
    # Memory implementations
    custom_memory = providers.Factory(CustomMemory)
    mongo_memory = providers.Factory(MongoMemory, config=config)
    
    # Brain provider (using the factory pattern)
    brain = providers.Factory(
        create_brain,
        config=config,
        chain_manager=chain_manager
    )
    
    # Bot provider
    bot = providers.Factory(
        Bot,
        brain=brain,
        memory=custom_memory,
        tools=providers.List([search_tool])
    )


# Create container instance
container = Container()


def get_memory(memory_type: str = "custom") -> BaseChatbotMemory:
    """
    Get a memory instance by type.
    
    Args:
        memory_type: Type of memory to use ("custom" or "mongo")
        
    Returns:
        Memory instance
    """
    if memory_type == "mongo":
        return container.mongo_memory()
    
    # Default to custom memory
    return container.custom_memory()


def get_bot(memory_type: str = "custom", tools: Optional[List[BaseTool]] = None) -> Bot:
    """
    Get a configured bot instance.
    
    Args:
        memory_type: Type of memory to use ("custom" or "mongo")
        tools: List of tools to provide to the bot
        
    Returns:
        Configured Bot instance
    """
    try:
        # Get memory instance
        memory = get_memory(memory_type)
        
        # Create list of tools
        tool_list = tools or [container.search_tool()]
        
        # Create the brain with the chain manager
        brain: BaseBrain = container.brain()
        
        # Create and return the bot
        bot_instance = Bot(
            brain=brain,
            memory=memory,
            tools=tool_list
        )
        
        logger.info(f"Created bot with memory_type={memory_type}")
        return bot_instance
        
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        # Fall back to default configuration
        return container.bot() 