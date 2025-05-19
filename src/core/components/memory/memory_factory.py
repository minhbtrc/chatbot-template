from src.core.components.memory.base import BaseChatbotMemory
from src.common.config import Config
from src.core.components.memory.clients.in_memory import InMemory
from src.core.components.memory.clients.mongodb_memory import MongoMemory


def create_memory(config: Config) -> BaseChatbotMemory:
    if config.bot_memory_type == "mongodb":
        return MongoMemory(config)
    elif config.bot_memory_type == "inmemory":
        return InMemory()
    else:
        raise ValueError(f"Invalid memory type: {config.bot_memory_type}")
