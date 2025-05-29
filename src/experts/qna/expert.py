"""
Bot module that handles message processing using a Brain for reasoning.
"""
from typing import Any

from injector import inject

from src.common.config import Config
from src.experts.base import BaseExpert
from src.base.brains import BrainInterface
from src.base.components import MemoryInterface, ToolProvider
from src.common.logging import logger
from .prompts import QNA_SYSTEM_PROMPT


class QnaExpert(BaseExpert):
    """
    Main bot class that handles message processing.
    
    The Bot is responsible for managing the message flow and delegating the
    reasoning to a Brain implementation. It uses a memory system to store
    conversation history.
    """
    @inject
    def __init__(
        self,
        config: Config,
        brain: BrainInterface,
        memory: MemoryInterface,
        tool_provider: ToolProvider,
    ):
        """
        Initialize the bot.
        
        Args:
            brain: Brain implementation for reasoning
            memory: Memory implementation for storing conversation history
            tool_provider: Provider for tools the bot can use
        """
        super().__init__(config, memory, brain)
        self.tool_provider = tool_provider
        logger.info(f"Bot initialized with brain type: {type(brain).__name__} and memory type: {type(memory).__name__}")

        available_tools = self.tool_provider.get_tools()
        if available_tools:
            logger.info(f"Binding {len(available_tools)} tools to brain")
            self.brain.use_tools(available_tools)
        else:
            logger.info("No tools available for binding")
    
    def _prepare_context(self, sentence: str, conversation_id: str, user_id: str, **kwargs: Any) -> str:
        """
        Prepare system message for the brain. It could be a prompt along with the retrieved chunks (RAG), ...
        
        Args:
            conversation_id: ID of the conversation
            sentence: User input
            user_id: ID of the user
            **kwargs: Additional arguments

        Returns:
            System message for the brain
        """
        return QNA_SYSTEM_PROMPT
    
    async def _aprepare_context(self, sentence: str, user_id: str, **kwargs: Any) -> str:
        """
        Prepare system message for the brain (asynchronous version).
        """
        return QNA_SYSTEM_PROMPT
