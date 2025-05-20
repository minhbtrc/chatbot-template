from src.common.config import Config
from .base import BaseChatbotMemory
from .variants.in_memory import InMemory
from .variants.mongodb_memory import MongoMemory


def create_memory(config: Config) -> BaseChatbotMemory:
    if config.bot_memory_type == "mongodb":
        return MongoMemory(config)
    elif config.bot_memory_type == "inmemory":
        return InMemory()
    else:
        raise ValueError(f"Invalid memory type: {config.bot_memory_type}")
