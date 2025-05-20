from abc import ABC, abstractmethod
from typing import List


class BaseVectorDatabase(ABC):
    """
    Base class for vector databases.
    """
    def __init__(self):
        pass

    @abstractmethod
    def index_documents(self, documents: List[str]) -> None:
        """
        Index a documents to the vector database.
        """
        pass

    @abstractmethod
    def retrieve_context(self, query: str, n_results: int = 10) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        pass

    @abstractmethod
    def delete_document(self, document: str) -> None:
        """
        Delete a document from the vector database.
        """
        pass
