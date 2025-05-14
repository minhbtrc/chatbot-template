"""
Retrieval Chain implementation.
This module provides a chain for retrieving information from documents.
"""

from typing import Dict, Any, List

from langchain.chains import RetrievalQA
from langchain.retrievers import BaseRetriever
from langchain.base_language import BaseLanguageModel

from infrastructure.config import Config


class RetrievalChain:
    """Chain for retrieving information from documents."""
    
    def __init__(
        self,
        config: Config,
        model: BaseLanguageModel,
        retriever: BaseRetriever,
        chain_type: str = "stuff",
        return_source_documents: bool = True,
    ):
        """
        Initialize the retrieval chain.
        
        Args:
            config: Application configuration
            model: Language model to use
            retriever: Document retriever
            chain_type: Type of chain to use (stuff, map_reduce, refine)
            return_source_documents: Whether to return source documents
        """
        self.config = config
        self.model = model
        self.retriever = retriever
        self.chain_type = chain_type
        self.return_source_documents = return_source_documents
        self.chain = self._create_chain()
    
    def _create_chain(self) -> RetrievalQA:
        """
        Create the retrieval chain.
        
        Returns:
            RetrievalQA chain
        """
        return RetrievalQA.from_chain_type(
            llm=self.model,
            chain_type=self.chain_type,
            retriever=self.retriever,
            return_source_documents=self.return_source_documents,
        )
    
    def call(self, query: str) -> Dict[str, Any]:
        """
        Call the retrieval chain with a query.
        
        Args:
            query: Query string
            
        Returns:
            Response from the chain
        """
        return self.chain(query)
    
    def get_relevant_documents(self, query: str) -> List[Any]:
        """
        Get relevant documents for a query.
        
        Args:
            query: Query string
            
        Returns:
            List of relevant documents
        """
        return self.retriever.get_relevant_documents(query) 