"""
Chat manager module that interfaces with experts.
"""

from typing import AsyncGenerator, Dict, Any
import asyncio

from injector import inject

from src.common.schemas import ChatResponse
from src.base.brains import BrainInterface
from src.experts import QnaExpert, RAGBotExpert
from src.common.config import Config
from src.common.logging import logger


class ChatEngine:
    """
    Chat engine that handles processing messages and managing conversations.
    This class serves as a bridge between the API and the expert implementations.
    """
    @inject
    def __init__(
        self,
        config: Config,
        brain: BrainInterface,
        qna_expert: QnaExpert,
        rag_bot_expert: RAGBotExpert
    ):
        """Initialize the chat engine with an expert instance."""
        # Create the config
        self.config = config
        # Create a brain based on the config
        self.brain = brain        
        self.qna_expert = qna_expert
        self.rag_bot_expert = rag_bot_expert
        self.current_expert = self.rag_bot_expert if config.expert_type == "RAG" else self.qna_expert
        logger.info(f"ChatEngine initialized with expert type: {config.expert_type}")
        logger.info(f"Expert class: {type(self.current_expert).__name__}")
    
    def get_current_expert_info(self) -> Dict[str, Any]:
        """
        Get information about the currently active expert.
        
        Returns:
            Dictionary containing current expert information
        """
        return self.current_expert.get_expert_info()
    
    def switch_expert(self, expert_type: str) -> None:
        """
        Switch to a different expert type.
        
        Args:
            expert_type: The new expert type to switch to
            
        Raises:
            ValueError: If the expert type is not supported
        """
        logger.info(f"Switching expert from {self.config.expert_type} to {expert_type}")
        
        # Update configuration
        old_expert_type = self.config.expert_type
        self.config.expert_type = expert_type
        
        try:
            # Create new expert instance
            self.current_expert = self.qna_expert if expert_type == "QNA" else self.rag_bot_expert
            logger.info(f"Successfully switched to expert type: {expert_type}")
        except Exception as e:
            # Rollback configuration on failure
            self.config.expert_type = old_expert_type
            logger.error(f"Failed to switch expert to {expert_type}: {str(e)}")
            raise
    
    async def process_message(
        self, 
        user_input: str, 
        conversation_id: str,
        user_id: str
    ) -> ChatResponse:
        """
        Process a user message and get a response.
        
        Args:
            user_input: User's message
            conversation_id: Optional conversation ID
            user_id: Optional user ID for authenticated users
            
        Returns:
            The expert's response
        """
        logger.info(f"Processing message for conversation {conversation_id} (user_id: {user_id})")
        logger.debug(f"User input: {user_input}")
        logger.debug(f"Using expert: {type(self.current_expert).__name__}")
        
        # Run the expert call in a thread pool to not block the event loop
        # as expert.process might be CPU intensive
        try:
            response = await asyncio.to_thread(
                self.current_expert.process,
                query=user_input,
                conversation_id=conversation_id,
                user_id=user_id
            )
            logger.info(f"Successfully processed message for conversation {conversation_id}")
            logger.debug(f"Expert response: {response.response}")
            
            return response
        except Exception as e:
            logger.error(f"Error processing message for conversation {conversation_id}: {str(e)}")
            raise
    
    async def stream_process_message(
        self, 
        user_input: str, 
        conversation_id: str,
        user_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Process a user message and stream the response.
        
        Args:
            user_input: User's message
            conversation_id: Optional conversation ID
            user_id: Optional user ID for authenticated users
            
        Yields:
            Chunks of the response content
        """
        # Generate conversation_id if not provided
        logger.info(f"Streaming message for conversation {conversation_id} (user_id: {user_id})")
        logger.debug(f"User input: {user_input}")
        logger.debug(f"Using expert: {type(self.current_expert).__name__}")
        
        try:
            # Stream the response from the expert
            async for chunk in self.current_expert.astream_call(
                sentence=user_input,
                user_id=user_id,
                conversation_id=conversation_id
            ):
                yield chunk

            logger.info(f"Successfully streamed message for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Error streaming message for conversation {conversation_id}: {str(e)}")
            raise
    
    def clear_history(self, conversation_id: str, user_id: str) -> None:
        """
        Clear the conversation history for a specific conversation.
        
        Args:
            conversation_id: ID of the conversation to clear
            user_id: User ID (not used in single user system)
        """
        logger.info(f"Clearing history for conversation {conversation_id}")
        self.current_expert.clear_history(conversation_id, user_id)
        logger.info(f"Successfully cleared history for conversation {conversation_id}")
    
    def get_all_conversations(self) -> list[str]:
        """
        Get all conversation IDs in the system.
        
        Returns:
            List of all conversation IDs
        """
        # Get all conversations from the current expert
        all_conversations = self.current_expert.get_all_conversations()
        
        logger.info(f"Found {len(all_conversations)} conversations")
        return all_conversations
    
    def close(self) -> None:
        """Close any resources used by the chat manager."""
        logger.info("Closing ChatEngine resources")
        self.current_expert.close()
        logger.info("ChatEngine resources closed successfully")
