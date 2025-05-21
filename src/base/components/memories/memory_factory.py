from src.common.config import Config
from .base import BaseChatbotMemory
from .variants.in_memory import InMemory
from .variants.mongodb_memory import MongoMemory


def create_memory(config: Config) -> BaseChatbotMemory:
    memory_type = config.bot_memory_type.upper() if config.bot_memory_type else None
    if memory_type == "MONGODB":
        return MongoMemory(config)
    elif memory_type == "INMEMORY":
        return InMemory()
    else:
        raise ValueError(f"Invalid memory type: {memory_type}")
