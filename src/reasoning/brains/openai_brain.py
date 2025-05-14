"""
OpenAI brain implementation module.

This module provides a brain implementation that uses OpenAI models.
"""

from typing import Dict, Any, Optional, List
import logging

from src.llms.clients.openai_client import OpenAIClient
from src.reasoning.brains.base import BaseBrain
from src.reasoning.chain_manager import ChainManager
from infrastructure.config import Config

logger = logging.getLogger(__name__)


class OpenAIBrain(BaseBrain):
    """Brain implementation using OpenAI models."""
    
    def __init__(
        self,
        config: Config,
        llm_client: OpenAIClient,
        model_kwargs: Optional[Dict[str, Any]] = None,
        chain_manager: Optional[ChainManager] = None,
    ):
        """
        Initialize the OpenAI brain.
        
        Args:
            config: Application configuration
            llm_client: OpenAI client instance
            model_kwargs: Optional model parameters
            chain_manager: Optional chain manager for structured reasoning
        """
        self.config = config
        self.llm_client = llm_client
        self.model_kwargs = model_kwargs or {}
        self.chain_manager = chain_manager
        self.tools = []
        
        # Create a standard chat chain if chain manager is provided
        if self.chain_manager:
            self.chat_chain_id = "openai_chat"
            self.chain_manager.create_chat_chain(self.chat_chain_id)
        
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the query using OpenAI and return a response.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Returns:
            Response from the OpenAI model
        """
        # If no context is provided, initialize it
        context = context or {}
        
        # Extract conversation history if available
        history = context.get("history", [])
        
        # Try to use chain manager if available and appropriate
        if self.chain_manager and not self.tools:
            try:
                # Use the chat chain for simple queries without tools
                return self.chain_manager.run_chain(
                    self.chat_chain_id, 
                    {"input": query, "history": history}
                )
            except Exception as e:
                logger.warning(f"Error using chain manager: {e}. Falling back to direct LLM call.")
        
        # Build messages for the chat
        messages: List[Dict[str, Any]] = []
        
        # Add system message if configuration has one
        if hasattr(self.config, "system_message") and self.config.system_message:
            messages.append({
                "role": "system",
                "content": self.config.system_message
            })
        
        # Add conversation history
        messages.extend(history)
        
        # Add the current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        # Log the messages being sent
        logger.debug(f"Sending messages to OpenAI: {messages}")
        
        # Call the OpenAI client
        response = self.llm_client.chat(messages, **self.model_kwargs)
        
        return response
    
    def reset(self) -> None:
        """Reset the brain state."""
        # For OpenAI, there's no local state to reset
        pass
    
    def use_tools(self, tools: List[Any]) -> None:
        """
        Configure the brain to use the provided tools.
        
        Args:
            tools: List of tools to use
        """
        self.tools = tools
        
    def get_info(self) -> Dict[str, Any]:
        """Get information about the brain."""
        info = super().get_info()
        info.update({
            "model_info": self.llm_client.get_model_info(),
            "tools_count": len(self.tools),
            "has_chain_manager": self.chain_manager is not None,
        })
        return info 