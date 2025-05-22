"""
Bot module that handles message processing using a Brain for reasoning.
"""
from typing import Dict, Any, Optional

from injector import inject

from src.common.schemas import ChatResponse
from src.base.brains import BrainInterface
from src.base.components import MemoryInterface, ToolProvider
from src.common.logging import logger


class Bot:
    """
    Main bot class that handles message processing.
    
    The Bot is responsible for managing the message flow and delegating the
    reasoning to a Brain implementation. It uses a memory system to store
    conversation history.
    """
    @inject
    def __init__(
        self,
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
        self.brain = brain
        self.memory = memory
        self.tool_provider = tool_provider
        logger.info(f"Bot initialized with brain type: {type(brain).__name__} and memory type: {type(memory).__name__}")

        available_tools = self.tool_provider.get_tools()
        if available_tools:
            logger.info(f"Binding {len(available_tools)} tools to brain")
            self.brain.use_tools(available_tools)
        else:
            logger.info("No tools available for binding")
    
    def _prepare_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Prepare the context for the brain.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Context for the brain
        """
        # Get conversation history from memory if available
        context: Dict[str, Any] = {}
        
        history = self.memory.get_history(conversation_id)
        if history:
            logger.debug(f"Retrieved {len(history)} messages from memory for conversation {conversation_id}")
            context["history"] = history
        else:
            logger.debug(f"No history found in memory for conversation {conversation_id}")
        return context
    
    def call(self, sentence: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
            conversation_id: ID for the conversation
            
        Returns:
            ChatResponse
        """
        if self.memory and conversation_id:
            logger.debug("Preparing context with conversation history")
            context = self._prepare_context(conversation_id)
        else:
            logger.debug("No memory or conversation_id provided, using empty context")
            context = {}
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = self.brain.think(sentence, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        if self.memory and conversation_id:
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
    
    async def acall(self, sentence: str, conversation_id: Optional[str] = None) -> ChatResponse:
        """
        Process a user message and generate a response.
        
        Args:
            sentence: User input
        """
        if self.memory and conversation_id:
            logger.debug("Preparing context with conversation history")
            context = self._prepare_context(conversation_id)
        else:
            logger.debug("No memory or conversation_id provided, using empty context")
            context = {}
            
        # Generate a response using the brain
        logger.debug("Generating response using brain")
        response = await self.brain.athink(sentence, context)
        logger.debug(f"Brain response generated: {response['content'][:100]}...")
        
        # Save the conversation to memory
        if self.memory and conversation_id:
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
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the bot.
        
        Returns:
            Dictionary with bot information
        """
        info = {
            "type": "Bot",
            "brain": self.brain.get_info(),
        }
        
        # Add memory info if available
        if self.memory:
            info["memory"] = {
                "type": self.memory.__class__.__name__
            }
            
        # Add tools info if available
        if self.tool_provider:
            info["tools"] = {
                "count": len(self.tool_provider.get_tools()),
                "types": [tool.__class__.__name__ for tool in self.tool_provider.get_tools()]
            }
        
        return info 

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
