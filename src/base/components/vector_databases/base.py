from abc import ABC, abstractmethod
from typing import List, Any

from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface


class BaseVectorDatabase(ABC):
    """
    Base class for vector databases.
    """
    def __init__(self, embeddings: EmbeddingsInterface):
        self.embeddings = embeddings

    @abstractmethod
    def _index_documents(self, documents_embeddings: List[Any]) -> None:
        """
        Index a documents to the vector database.
        """
        pass

    def index_documents(self, documents: List[str]) -> None:
        """
        Index a documents to the vector database.
        """
        documents_embeddings = self.embeddings.process_documents(documents)
        self._index_documents(documents_embeddings)
    
    @abstractmethod
    def _retrieve_context(self, query_embedding: Any, n_results: int = 10) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        pass

    def retrieve_context(self, query: str, n_results: int = 10) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        query_embedding = self.embeddings.process(query)
        return self._retrieve_context(query_embedding, n_results)

    @abstractmethod
    def delete_document(self, document: str) -> None:
        """
        Delete a document from the vector database.
        """
        pass
