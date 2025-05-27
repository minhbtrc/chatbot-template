"""
Bot module that handles message processing using a Brain for reasoning.
"""
from typing import Dict, Any, Generator, AsyncGenerator, List

from injector import inject

from src.common.config import Config
from src.experts.base import BaseExpert
from src.common.schemas import ChatResponse
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
    
    def _prepare_history(self, sentence: str, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Prepare the context for the brain.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Context for the brain
        """
        self.memory.add_message(
            role="user",
            content=sentence,
            conversation_id=conversation_id
        )
        # Get conversation history from memory if available
        history = self.memory.get_history(conversation_id)
        if not history:
            logger.debug(f"No history found in memory for conversation {conversation_id}")
            history = []
        return history
    
    def _prepare_context(self, sentence: str, conversation_id: str) -> str:
        """
        Prepare system message for the brain. It could be a prompt along with the retrieved chunks (RAG), ...
        
        Args:
            conversation_id: ID of the conversation
            sentence: User input

        Returns:
            System message for the brain
        """
        return QNA_SYSTEM_PROMPT
    
    def call(self, sentence: str, conversation_id: str) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
            conversation_id: ID for the conversation
            
        Returns:
            ChatResponse
        """
        history = self._prepare_history(sentence, conversation_id)
        context = self._prepare_context(sentence, conversation_id)
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = self.brain.think(history, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_messages(
            [
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": response["content"]}
            ],
            conversation_id
        )
        logger.debug("Conversation saved to memory")
        
        # Return a structured response
        return ChatResponse(
            response=response["content"],
            conversation_id=conversation_id or "default",
            additional_kwargs=response["additional_kwargs"]
        )
    
    def stream_call(self, sentence: str, conversation_id: str, user_id: str) -> Generator[str, None, None]:
        """
        Process a user message and stream the response.
        
        Args:
            sentence: User input
            conversation_id: ID for the conversation
            
        Yields:
            Chunks of the response content
        """
        history = self._prepare_history(sentence, conversation_id)
        context = self._prepare_context(sentence, conversation_id)
            
        # Generate a streaming response using the brain
        logger.debug("Generating streaming response using brain")
        full_response = ""
        
        for chunk in self.brain.stream_think(history, context):
            full_response += chunk
            yield chunk
        
        logger.debug(f"Brain streaming response completed: {full_response[:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_messages(
            [
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": full_response}
            ],
            conversation_id
        )
        logger.debug("Conversation saved to memory")

    async def acall(self, sentence: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
        """
        history = self._prepare_history(sentence, conversation_id)
        context = self._prepare_context(sentence, conversation_id)
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = await self.brain.athink(history, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_messages(
            [
                {"role": "user", "content": sentence},  
                {"role": "assistant", "content": response["content"]}
            ],
            conversation_id
        )
        logger.debug("Conversation saved to memory")
        
        # Return a structured response
        return ChatResponse(
            response=response["content"],
            conversation_id=conversation_id or "default",
            additional_kwargs=response["additional_kwargs"]
        )
    
    async def astream_call(self, sentence: str, conversation_id: str, user_id: str) -> AsyncGenerator[str, None]:
        """
        Process a user message and stream the response asynchronously.
        
        Args:
            sentence: User input
            conversation_id: ID for the conversation
            
        Yields:
            Chunks of the response content
        """
        history = self._prepare_history(sentence, conversation_id)
        context = self._prepare_context(sentence, conversation_id)

        # Generate a streaming response using the brain
        logger.debug("Generating async streaming response using brain")
        full_response = ""
        
        async for chunk in self.brain.astream_think(history, context):
            full_response += chunk
            yield chunk
        
        logger.debug(f"Brain async streaming response completed: {full_response[:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_messages(
            [
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": full_response}
            ],
            conversation_id
        )
        logger.debug("Conversation saved to memory")
    
    def reset_history(self, conversation_id: str) -> None:
        """
        Reset the conversation history.
        
        Args:
            conversation_id: ID of the conversation to reset
        """
        logger.info(f"Resetting history for conversation {conversation_id}")
        if self.memory:
            logger.debug("Clearing memory history")
            self.memory.clear_history(conversation_id)
            logger.debug("Memory history cleared")
        
        # Also reset the brain state
        logger.debug("Resetting brain state")
        self.brain.reset()
        logger.info(f"Successfully reset history for conversation {conversation_id}")
