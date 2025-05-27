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

    @abstractmethod
    def process(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Process a query and return a response.
        
        Args:
            query: User input query
            conversation_id: ID of the conversation
            
        Returns:
            ChatResponse containing the expert's response
        """
        pass

    @abstractmethod
    async def aprocess(self, query: str, conversation_id: str, user_id: str) -> ChatResponse:
        """
        Asynchronously process a query and return a response.
        
        Args:
            query: User input query
            conversation_id: ID of the conversation
            
        Returns:
            ChatResponse containing the expert's response
        """
        pass

    @abstractmethod
    def clear_history(self, conversation_id: str, user_id: str) -> None:
        """
        Clear the conversation history for a specific conversation.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        pass
    
    def stream_call(self, sentence: str, conversation_id: str, user_id: str) -> Generator[str, None, None]:
        """
        Stream a response to user input (synchronous version).
        Default implementation falls back to non-streaming.
        
        Args:
            sentence: User input
            user_id: ID of the user
            conversation_id: ID of the conversation
            
        Yields:
            Chunks of the response content
        """
        response = self.process(sentence, conversation_id, user_id)
        yield response.response
    
    async def astream_call(self, sentence: str, conversation_id: str, user_id: str) -> AsyncGenerator[str, None]:
        """
        Stream a response to user input (asynchronous version).
        Default implementation falls back to non-streaming.
        
        Args:
            sentence: User input
            user_id: ID of the user
            conversation_id: ID of the conversation
            
        Yields:
            Chunks of the response content
        """
        response = await self.aprocess(sentence, conversation_id, user_id)
        yield response.response

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
        if hasattr(self.memory, 'close'):
            logger.debug("Closing memory resources")
            self.memory.close()
        if hasattr(self.brain, 'close'):
            logger.debug("Closing brain resources")
            getattr(self.brain, 'close')()
        logger.info("Bot resources closed successfully")