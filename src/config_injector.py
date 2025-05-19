from injector import Binder, Injector, Module, singleton

from src.common.config import Config
from src.core.components import create_llm_client, LLMInterface, create_memory, MemoryInterface, ToolProvider
from src.core.bot import Bot
from src.chat_engine import ChatEngine
from src.core.brains import BrainInterface, create_brain
# Global injector instance
_global_injector = None


# Configurable module
class ConfigurableModule(Module):
    def __init__(self, config: Config):
        self.config = config

    def configure(self, binder: Binder):
        binder.bind(Config, to=self.config)

        llm_client = create_llm_client(self.config)
        binder.bind(LLMInterface, to=llm_client, scope=singleton)

        memory = create_memory(self.config)
        binder.bind(MemoryInterface, to=memory, scope=singleton)

        # Create and bind the tool provider
        tool_provider = ToolProvider()
        binder.bind(ToolProvider, to=tool_provider, scope=singleton)
        
        brain = create_brain(self.config, llm_client, tool_provider)
        binder.bind(BrainInterface, to=brain, scope=singleton)

        binder.bind(Bot, to=Bot, scope=singleton)
        binder.bind(ChatEngine, to=ChatEngine, scope=singleton)


def update_injector_with_config(config: Config):
    global _global_injector
    _global_injector = Injector([ConfigurableModule(config)])
    return _global_injector


def get_instance(_cls): # type: ignore
    global _global_injector
    if _global_injector is None:
        raise Exception("Injector is not initialized. Call update_injector_with_config(config) first.")
    return _global_injector.get(_cls) # type: ignore