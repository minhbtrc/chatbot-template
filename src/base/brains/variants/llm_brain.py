"""
LLM brain implementation module.

This module provides a LLM brain implementation that can switch between
different LLM providers based on configuration.
"""

from typing import Dict, Any, Optional, List, Generator, AsyncGenerator

from injector import inject

from src.base.components import LLMInterface
from src.base.brains.base import BaseBrain
from src.common.config import Config
from src.common.logging import logger
from src.base.components.tools import BaseTool


class LLMBrain(BaseBrain):
    """
    LLM brain implementation that can use different LLM clients.
    
    This brain can switch between different LLM providers based on configuration.
    """
    @inject
    def __init__(
        self,
        config: Config,
        llm_client: LLMInterface,
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
    
    def _build_messages(
        self,
        history: List[Dict[str, Any]],
        system_message: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """ Build messages for the chat """
        messages: List[Dict[str, Any]] = []
        
        # Add system message if configuration has one
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # Add conversation history
        messages.extend(history)
        
        return messages
    
    def think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the query using the configured LLM and return a response.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Returns:
            Response from the LLM
        """
        messages = self._build_messages(history, system_message)
        
        # Log the messages being sent
        logger.debug(f"Sending messages to {self.llm_type}: {messages}")
        
        # Call the LLM client
        response = self.llm_client.chat(messages, **kwargs)
        
        return response
    
    async def athink(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the query using the configured LLM and return a response.
        """
        messages = self._build_messages(history, system_message)
        
        # Log the messages being sent
        logger.debug(f"Sending messages to {self.llm_type}: {messages}")
        
        # Call the LLM client
        response = await self.llm_client.achat(messages, **kwargs)
        
        return response
    
    def stream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Generator[str, None, None]:
        """
        Process the query using the configured LLM and stream the response.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Yields:
            Chunks of the response content
        """
        messages = self._build_messages(history, system_message)
        
        # Log the messages being sent
        logger.debug(f"Streaming messages to {self.llm_type}: {messages}")
        
        for chunk in self.llm_client.stream_chat(messages, **kwargs):
            yield chunk
    
    async def astream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Process the query using the configured LLM and stream the response asynchronously.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Yields:
            Chunks of the response content
        """
        messages = self._build_messages(history, system_message)
        
        # Log the messages being sent
        logger.debug(f"Async streaming messages to {self.llm_type}: {messages}")
        
        async for chunk in self.llm_client.astream_chat(messages, **kwargs):
            yield chunk
    
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