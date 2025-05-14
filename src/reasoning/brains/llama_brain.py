"""
Llama brain implementation module.

This module provides a brain implementation that uses Llama models via llama.cpp.
"""

from typing import Dict, Any, Optional, List
import logging

from src.reasoning.brains.base import BaseBrain
from infrastructure.config import Config

logger = logging.getLogger(__name__)


class LlamaBrain(BaseBrain):
    """Brain implementation using Llama models."""
    
    def __init__(
        self,
        config: Config,
        llm_client: Any,
        model_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Llama brain.
        
        Args:
            config: Application configuration
            llm_client: LlamaCpp client instance
            model_kwargs: Optional model parameters
        """
        self.config = config
        self.llm_client = llm_client
        self.model_kwargs = model_kwargs or {}
        self.tools = []
    
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process the query using Llama and return a response.
        
        Args:
            query: The user's input query
            context: Optional context containing conversation history, etc.
            
        Returns:
            Response from the Llama model
        """
        # If no context is provided, initialize it
        context = context or {}
        
        # Extract conversation history if available
        history = context.get("history", [])
        
        # Convert chat history to a format Llama can understand
        prompt = self._format_prompt(query, history)
        
        # Log the prompt being sent
        logger.debug(f"Sending prompt to Llama: {prompt}")
        
        # Call the Llama client
        response = self.llm_client.complete(prompt, **self.model_kwargs)
        
        return response
    
    def _format_prompt(self, query: str, history: List[Dict[str, str]]) -> str:
        """
        Format the prompt for Llama models including conversation history.
        
        Args:
            query: The current query
            history: List of conversation history messages
            
        Returns:
            Formatted prompt string
        """
        formatted_history = ""
        
        for message in history:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "user":
                formatted_history += f"Human: {content}\n"
            elif role == "assistant":
                formatted_history += f"Assistant: {content}\n"
            # Ignore system messages for now
        
        # Add the current query
        formatted_prompt = f"{formatted_history}Human: {query}\nAssistant:"
        
        return formatted_prompt
    
    def reset(self) -> None:
        """Reset the brain state."""
        # For Llama, there's no persistent state to reset
        pass
    
    def use_tools(self, tools: List[Any]) -> None:
        """
        Configure the brain to use the provided tools.
        
        Args:
            tools: List of tools to use
        """
        self.tools = tools
        # Tool support would require custom implementation for Llama
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the brain."""
        info = super().get_info()
        info.update({
            "model_info": self.llm_client.get_model_info(),
            "tools_count": len(self.tools),
        })
        return info 