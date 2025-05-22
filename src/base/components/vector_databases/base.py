from abc import ABC, abstractmethod
from typing import List

from langchain_core.documents import Document

from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface


class BaseVectorDatabase(ABC):
    """
    Base class for vector databases.
    """
    def __init__(self, embeddings: EmbeddingsInterface):
        self.embeddings = embeddings

    @abstractmethod
    def _index_documents(self, documents: List[Document]) -> None:
        """
        Index a documents to the vector database.
        """
        pass

    def index_documents(self, documents: List[Document]) -> None:
        """
        Index a documents to the vector database.
        """
        self._index_documents(documents)

    @abstractmethod
    async def _aindex_documents(self, documents: List[Document]) -> None:
        """
        Index a documents to the vector database.
        """
        pass

    async def aindex_documents(self, documents: List[Document]) -> None:
        """
        Index a documents to the vector database.
        """
        await self._aindex_documents(documents)
    
    @abstractmethod
    def _retrieve_context(self, query: str, n_results: int = 10) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        pass

    def retrieve_context(self, query: str, n_results: int = 10) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        return self._retrieve_context(query, n_results)

    @abstractmethod
    def delete_document(self, document: str) -> None:
        """
        Delete a document from the vector database.
        """
        pass
