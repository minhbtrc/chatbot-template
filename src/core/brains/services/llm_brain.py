"""
LLM brain implementation module.

This module provides a LLM brain implementation that can switch between
different LLM providers based on configuration.
"""

from typing import Dict, Any, Optional, List

from injector import inject

from src.core.components.llms.base import BaseLLMClient
from src.core.brains.base import BaseBrain
from src.common.config import Config
from src.common.logging import logger
from src.core.components.tools import BaseTool

class LLMBrain(BaseBrain):
    """
    LLM brain implementation that can use different LLM clients.
    
    This brain can switch between different LLM providers based on configuration.
    """
    @inject
    def __init__(
        self,
        config: Config,
        llm_client: BaseLLMClient,
    ):
        """
        Initialize the LLM brain.
        
        Args:
            config: Application configuration
            llm_client: LLM client instance
        """
        self.config = config
        self.llm_client = llm_client
        self.tools: List[BaseTool] = []
        
        # Determine LLM type from config or parameter
        self.llm_type = config.model_type or "azureopenai"
    
    def think(self, query: str, context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the query using the configured LLM and return a response.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Returns:
            Response from the LLM
        """
        # If no context is provided, initialize it
        context = context or {}
        
        # Extract conversation history if available
        history = context.get("history", [])
        
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
        logger.debug(f"Sending messages to {self.llm_type}: {messages}")
        
        # Call the LLM client
        response = self.llm_client.chat(messages, **kwargs)
        
        return response
    
    def reset(self) -> None:
        """Reset the brain state."""
        # For most LLMs, there's no local state to reset
        pass
    
    def use_tools(self, tools: Optional[List[Any]] = None) -> None:
        """
        Configure the brain to use the provided tools.
        
        Args:
            tools: List of tools to use
        """
        logger.warning("Using tools with LLM brain will only generate tool calls as additional kwargs, the LLM itself doesn't execute the tools.")
        self.llm_client.bind_tools(tools)
        
    def get_info(self) -> Dict[str, Any]:
        """Get information about the brain."""
        info = super().get_info()
        info.update({
            "llm_type": self.llm_type,
            "model_info": self.llm_client.get_model_info(),
            "tools_count": len(self.tools),
        })
        return info 