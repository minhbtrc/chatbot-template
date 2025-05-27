from typing import Optional

from src.common.config import Config
from .base import BaseChatbotMemory
from .variants.in_memory import InMemory
from .variants.mongodb_memory import MongoMemory
from .variants.sql_memory import SQLMemory


def create_memory(config: Config, user_id: Optional[int] = None) -> BaseChatbotMemory:
    """
    Create a memory instance based on configuration.
    
    Args:
        config: Application configuration
        user_id: Optional user ID to associate with the memory instance
        
    Returns:
        Memory instance
    """
    memory_type = config.bot_memory_type.upper() if config.bot_memory_type else None
    
    if memory_type == "MONGODB":
        return MongoMemory(config)
    elif memory_type == "INMEMORY":
        return InMemory()
    elif memory_type == "SQL":
        return SQLMemory(user_id=user_id)
    else:
        raise ValueError(f"Invalid memory type: {memory_type}. Supported types: MONGODB, INMEMORY, SQL, ASYNC_SQL")
