from abc import abstractmethod
from typing import AsyncGenerator, Generator, Dict, Any, List

from injector import inject
from loguru import logger

from src.common.config import Config
from src.common.schemas import ChatResponse
from src.base.components import MemoryInterface
from src.base.brains import BrainInterface


class BaseExpert:
    @inject
    def __init__(self, config: Config, memory: MemoryInterface, brain: BrainInterface):
        self.config = config
        self.memory = memory
        self.brain = brain

    def process(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
            conversation_id: ID for the conversation
            
        Returns:
            ChatResponse
        """
        history = self._prepare_history(query, conversation_id, user_id)
        context = self._prepare_context(query, conversation_id, user_id)
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = self.brain.think(history, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_message(
            role="assistant", content=response["content"], conversation_id=conversation_id
        )
        logger.debug("Conversation saved to memory")
        # Return a structured response
        return ChatResponse(
            response=response["content"],
            conversation_id=conversation_id or "default",
            additional_kwargs=response["additional_kwargs"]
        )

    async def aprocess(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
        """
        history = self._prepare_history(query, conversation_id, user_id)
        context = await self._aprepare_context(query, user_id)
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = await self.brain.athink(history, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        logger.debug("Saving conversation to memory")
        self.memory.add_message(
            role="assistant", content=response["content"], conversation_id=conversation_id
        )
        logger.debug("Conversation saved to memory")
        
        # Return a structured response
        return ChatResponse(
            response=response["content"],
            conversation_id=conversation_id or "default",
            additional_kwargs=response["additional_kwargs"]
        )

    def clear_history(self, conversation_id: str, user_id: str) -> None:
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

    def _prepare_history(self, sentence: str, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
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

    @abstractmethod
    def _prepare_context(self, sentence: str, conversation_id: str, user_id: str, **kwargs: Any) -> str:
        """
        Prepare the context for the brain.
        """
        pass
    
    @abstractmethod
    async def _aprepare_context(self, sentence: str, user_id: str) -> str:
        """
        Prepare the context for the brain (asynchronous version).
        """
        pass

    def stream_call(self, sentence: str, conversation_id: str, user_id: str) -> Generator[str, None, None]:
        """
        Stream a response to user input using RAG context.
        
        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            
        Yields:
            Chunks of the response content
        """
        history = self._prepare_history(sentence, conversation_id, user_id)
        context = self._prepare_context(sentence, conversation_id, user_id)
        
        # Generate a streaming response using the brain
        logger.debug("Generating streaming response using brain")
        full_response = ""
        
        for chunk in self.brain.stream_think(history, context):
            full_response += chunk
            yield chunk
        
        logger.debug(f"Brain streaming response completed: {full_response[:100]}...")
        
        # Save the assistant message to memory
        logger.debug("Saving assistant message to memory")
        self.memory.add_message(
            role="assistant", content=full_response, conversation_id=conversation_id
        )
        logger.debug("Assistant message saved to memory")
    
    async def astream_call(self, sentence: str, conversation_id: str, user_id: str) -> AsyncGenerator[str, None]:
        """
        Stream a response to user input using RAG context (asynchronous).
        
        Args:
            sentence: User input
            conversation_id: ID of the conversation
            user_id: ID of the user
            
        Yields:
            Chunks of the response content
        """
        history = self._prepare_history(sentence, conversation_id, user_id)
        context = await self._aprepare_context(sentence, user_id)
        
        # Generate a streaming response using the brain
        logger.debug("Generating async streaming response using brain")
        full_response = ""
        
        async for chunk in self.brain.astream_think(history, context):
            full_response += chunk
            yield chunk
        
        logger.debug(f"Brain async streaming response completed: {full_response[:100]}...")
        
        # Save the assistant message to memory
        logger.debug("Saving assistant message to memory")
        self.memory.add_message(
            role="assistant", content=full_response, conversation_id=conversation_id
        )
        logger.debug("Assistant message saved to memory")

    def get_expert_info(self) -> Dict[str, Any]:
        """
        Get information about the expert.
        
        Returns:
            Dictionary containing expert information
        """
        return {
            "expert_type": self.__class__.__name__
        }

    def get_all_conversations(self) -> List[str]:
        """
        Get all conversation IDs for the expert.
        
        Returns:
            List of conversation IDs
        """
        return self.memory.get_all_conversations()
    
    def close(self) -> None:
        """Close any resources used by the bot."""
        logger.info("Closing bot resources")
        logger.debug("Closing memory resources")
        self.memory.close()
        logger.debug("Closing brain resources")
        self.brain.close()
        logger.info("Bot resources closed successfully")