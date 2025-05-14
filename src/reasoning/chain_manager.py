"""
Chain manager module for the reasoning system.

This module provides utilities for creating and managing language model chains
that can be used by Brain implementations.
"""

from typing import Dict, Any, Optional, List, Sequence, TypedDict

from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseMemory

from src.llms.base import BaseLLMClient
from infrastructure.logging import logger


class Message(TypedDict):
    """Message structure for chat interfaces."""
    role: str
    content: str


class LangChainAdapter:
    """Adapter class to convert between LangChain and our LLM client interfaces."""
    
    def __init__(self, client: BaseLLMClient):
        """Initialize the adapter with an LLM client."""
        self.client = client
    
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Handle completion-style requests."""
        return self.client.complete(prompt, **kwargs)
    
    def chat(self, messages: Sequence[Any], **kwargs: Any) -> str:
        """
        Handle chat-style requests by converting LangChain messages.
        
        Args:
            messages: LangChain message objects with type and content attributes
            kwargs: Additional parameters for the LLM client
            
        Returns:
            LLM response
        """
        # Convert LangChain message format to our format (compatible with BaseLLMClient.chat)
        converted_messages: List[Dict[str, str]] = [
            {"role": getattr(msg, "type", "user"), "content": getattr(msg, "content", str(msg))}
            for msg in messages
        ]
        return self.client.chat(converted_messages, **kwargs)
    
    def __call__(self, prompt_or_messages: Any, **kwargs: Any) -> str:
        """
        Handle both completion and chat interfaces.
        
        This method detects whether it's being called with a string (completion)
        or messages (chat) and routes accordingly.
        
        Args:
            prompt_or_messages: Either a string prompt or a list of messages
            kwargs: Additional parameters for the LLM client
            
        Returns:
            LLM response
        """
        if isinstance(prompt_or_messages, str):
            return self.complete(prompt_or_messages, **kwargs)
        else:
            return self.chat(prompt_or_messages, **kwargs)


class ChainManager:
    """
    Manager for language model chains.
    
    This class creates and manages langchain chains that can be used by
    Brain implementations for structured reasoning flows.
    """
    
    def __init__(
        self,
        llm_client: BaseLLMClient,
        prompt_template: Optional[str] = None,
        memory: Optional[BaseMemory] = None,
        verbose: bool = False
    ):
        """
        Initialize the chain manager.
        
        Args:
            llm_client: LLM client to use
            prompt_template: Custom prompt template (optional)
            memory: Memory implementation (optional)
            verbose: Whether to enable verbose output
        """
        self.llm_client = llm_client
        self.memory = memory
        self.verbose = verbose
        self.prompt_template = prompt_template or self.default_prompt_template()
        self.chains: Dict[str, LLMChain] = {}
        # Create the adapter once
        self.llm_adapter = LangChainAdapter(self.llm_client)
        
    def default_prompt_template(self) -> str:
        """
        Get the default prompt template.
        
        Returns:
            Default prompt template
        """
        return """
You are a helpful assistant designed to provide informative responses.

Context information is below.
---------------------
{context}
---------------------

Given the context information and not prior knowledge, answer the question: {question}
"""
    
    def create_chain(self, chain_id: str, input_variables: Optional[List[str]] = None) -> LLMChain:
        """
        Create a language model chain.
        
        Args:
            chain_id: Identifier for the chain
            input_variables: Variables expected in the prompt template
            
        Returns:
            LLMChain instance
        """
        # Use default input variables if none provided
        if input_variables is None:
            input_variables = ["context", "question"]
        
        # Create prompt template
        prompt = PromptTemplate(
            input_variables=input_variables,
            template=self.prompt_template
        )
        
        # Create chain parameters
        chain_kwargs: Dict[str, Any] = {
            "llm": self.llm_adapter,
            "prompt": prompt,
            "verbose": self.verbose,
        }
        
        # Add memory if provided
        if self.memory:
            chain_kwargs["memory"] = self.memory
        
        # Create and store the chain
        chain = LLMChain(**chain_kwargs)
        self.chains[chain_id] = chain
        
        logger.info(f"Created chain with ID: {chain_id}")
        return chain
    
    def get_chain(self, chain_id: str) -> Optional[LLMChain]:
        """
        Get a chain by ID.
        
        Args:
            chain_id: Identifier for the chain
            
        Returns:
            LLMChain instance or None if not found
        """
        return self.chains.get(chain_id)
    
    def run_chain(self, chain_id: str, inputs: Dict[str, Any]) -> str:
        """
        Run a chain with the given inputs.
        
        Args:
            chain_id: Identifier for the chain
            inputs: Input variables
            
        Returns:
            Output from the chain
            
        Raises:
            ValueError: If the chain is not found
        """
        chain = self.get_chain(chain_id)
        if not chain:
            raise ValueError(f"Chain with ID '{chain_id}' not found")
            
        return chain.run(inputs)
    
    def create_chat_chain(self, chain_id: str) -> LLMChain:
        """
        Create a chat-based language model chain.
        
        Args:
            chain_id: Identifier for the chain
            
        Returns:
            LLMChain instance
        """
        # Create message templates directly to avoid type issues with from_messages
        system_message = SystemMessagePromptTemplate.from_template(self.prompt_template)
        human_message = HumanMessagePromptTemplate.from_template("{input}")
        
        # Combine the templates into a chat prompt
        chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
        
        # Create chain parameters
        chain_kwargs: Dict[str, Any] = {
            "llm": self.llm_adapter,
            "prompt": chat_prompt,
            "verbose": self.verbose,
        }
        
        # Add memory if provided
        if self.memory:
            chain_kwargs["memory"] = self.memory
        
        # Create and store the chain
        chain = LLMChain(**chain_kwargs)
        self.chains[chain_id] = chain
        
        logger.info(f"Created chat chain with ID: {chain_id}")
        return chain 