from abc import ABC, abstractmethod
from typing import List, Dict, Any

from langchain_core.documents import Document

from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface


class BaseVectorDatabase(ABC):
    """
    Base class for vector databases.
    """
    def __init__(self, embeddings: EmbeddingsInterface):
        self.embeddings = embeddings

    def make_metadata_filter(self, metadata: Dict[str, Any]):
        """
        Make a metadata filter for the vector database.
        """
        def filter_fn(doc: Document) -> bool:
            for key, value in metadata.items():
                if isinstance(value, list):
                    if doc.metadata.get(key) not in value:
                        return False
                else:
                    if doc.metadata.get(key) != value:
                        return False
            return True
        return filter_fn

    @abstractmethod
    def _index_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        pass

    def index_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        return self._index_documents(documents)

    @abstractmethod
    async def _aindex_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        pass

    async def aindex_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        return await self._aindex_documents(documents)
    
    @abstractmethod
    def _retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        pass

    def retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        return self._retrieve_context(query, n_results, metadata)
    
    @abstractmethod
    async def _aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        pass

    async def aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        return await self._aretrieve_context(query, n_results, metadata)

    @abstractmethod
    def delete_document(self, document: str) -> None:
        """
        Delete a document from the vector database.
        """
        pass
