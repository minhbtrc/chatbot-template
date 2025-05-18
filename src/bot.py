"""
Bot module that handles message processing using a Brain for reasoning.
"""
from typing import Dict, Any, Optional

from injector import inject

from src.common.schemas import ChatResponse
from src.reasoning.brains.base import BaseBrain
from src.components.memory.base import BaseChatbotMemory
from src.components.tools import ToolProvider


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
        brain: BaseBrain,
        memory: BaseChatbotMemory,
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
            context["history"] = history
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
            context = self._prepare_context(conversation_id)
        else:
            context = {}
        # Generate a response using the brain
        response = self.brain.think(sentence, context)
        
        # Save the conversation to memory
        if self.memory and conversation_id:
            self.memory.add_messages(
                [
                    {"role": "user", "content": sentence},
                    {"role": "assistant", "content": response}
                ],
                conversation_id
            )
        
        # Return a structured response
        return ChatResponse(
            response=response,
            conversation_id=conversation_id or "default"
        )
    
    def reset_history(self, conversation_id: str) -> None:
        """
        Reset the conversation history.
        
        Args:
            conversation_id: ID of the conversation to reset
        """
        if self.memory:
            self.memory.clear_history(conversation_id)
        
        # Also reset the brain state
        self.brain.reset()
    
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
