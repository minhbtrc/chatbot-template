"""
Chain manager module.

This module provides functionality to create and manage language model chains.
"""

from typing import Dict, Any, Optional, Union

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import BaseLLM
from langchain.schema import BaseMemory


class ChainManager:
    """
    Manager for language model chains.
    
    This class handles the creation and execution of language model chains,
    providing a unified interface for different types of chains.
    """
    
    def __init__(
        self,
        llm: Union[BaseChatModel, BaseLLM],
        prompt_template: Optional[str] = None,
        memory: Optional[BaseMemory] = None,
        verbose: bool = False
    ):
        """
        Initialize the chain manager.
        
        Args:
            llm: Language model to use
            prompt_template: Custom prompt template (optional)
            memory: Memory implementation (optional)
            verbose: Whether to enable verbose output
        """
        self.llm = llm
        self.memory = memory
        self.verbose = verbose
        self.prompt_template = prompt_template or self.default_prompt_template()
        self.chain = self._create_chain()
    
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
    
    def _create_chain(self) -> LLMChain:
        """
        Create a language model chain.
        
        Returns:
            LLMChain instance
        """
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.prompt_template
        )
        
        chain_kwargs: Dict[str, Any] = {
            "llm": self.llm,
            "prompt": prompt,
            "verbose": self.verbose,
        }
        
        # Add memory if provided
        if self.memory:
            chain_kwargs["memory"] = self.memory
        
        return LLMChain(**chain_kwargs)
    
    def run(self, input_text: str, context: str = "") -> str:
        """
        Run the chain on input text.
        
        Args:
            input_text: Text to process
            context: Additional context (optional)
            
        Returns:
            Output from the chain
        """
        inputs = {
            "question": input_text,
            "context": context or ""
        }
        
        return self.chain.run(inputs)
    
    def generate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate outputs from the chain.
        
        Args:
            inputs: Input variables
            
        Returns:
            Output dictionary
        """
        return self.chain.generate([inputs]) 