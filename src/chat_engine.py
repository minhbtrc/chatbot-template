"""
Chat manager module that interfaces with the bot.
"""

from typing import Optional
import asyncio

from injector import inject

from src.common.schemas import ChatResponse
from src.base.brains import BrainInterface
from src.base.bot import Bot
from src.common.config import Config
from src.common.logging import logger


class ChatEngine:
    """
    Chat engine that handles processing messages and managing conversations.
    This class serves as a bridge between the API and the bot implementation.
    """
    @inject
    def __init__(
        self,
        config: Config,
        brain: BrainInterface,
        bot: Bot,
    ):
        """Initialize the chat engine with a bot instance."""
        # Create the config
        self.config = config
        # Create a brain based on the config
        self.brain = brain        
        # Create bot instance
        self.bot = bot
        logger.info(f"ChatEngine initialized with brain type: {type(brain).__name__}")
    
    async def process_message(self, user_input: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """
        Process a user message and get a response.
        
        Args:
            user_input: User's message
            conversation_id: Optional conversation ID
            
        Returns:
            The bot's response
        """
        # Use conversation_id or default
        conversation_id = conversation_id or "default"
        logger.info(f"Processing message for conversation {conversation_id}")
        logger.debug(f"User input: {user_input}")
        
        # Run the bot call in a thread pool to not block the event loop
        # as bot.call might be CPU intensive
        try:
            response = await asyncio.to_thread(
                self.bot.call,
                sentence=user_input,
                conversation_id=conversation_id
            )
            logger.info(f"Successfully processed message for conversation {conversation_id}")
            logger.debug(f"Bot response: {response.response}")
            return response
        except Exception as e:
            logger.error(f"Error processing message for conversation {conversation_id}: {str(e)}")
            raise
    
    def clear_history(self, conversation_id: str) -> None:
        """
        Clear the conversation history for a specific conversation.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        logger.info(f"Clearing history for conversation {conversation_id}")
        self.bot.reset_history(conversation_id)
        logger.info(f"Successfully cleared history for conversation {conversation_id}")
    
    def close(self) -> None:
        """Close any resources used by the chat manager."""
        logger.info("Closing ChatEngine resources")
        self.bot.close()
        logger.info("ChatEngine resources closed successfully")
