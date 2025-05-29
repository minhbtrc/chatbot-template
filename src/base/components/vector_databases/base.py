from abc import ABC
from typing import List, Dict, Any

from loguru import logger
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface


class BaseVectorDatabase(ABC):
    """
    Base class for vector databases.
    """
    def __init__(self, embeddings: EmbeddingsInterface):
        self.embeddings = embeddings
        self.client: VectorStore

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

    def _index_documents(self, documents: List[Document]) -> List[str]:
        return self.client.add_documents(documents)

    def index_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        return self._index_documents(documents)
    
    async def _aindex_documents(self, documents: List[Document]) -> List[str]:
        return await self.client.aadd_documents(documents)

    async def aindex_documents(self, documents: List[Document]) -> List[str]:
        """
        Index a documents to the vector database.
        """
        return await self._aindex_documents(documents)
    
    def _retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.client.as_retriever(
            search_kwargs={"k": n_results}
        )
        return [doc.page_content for doc in retriever.invoke(query, filter=self.make_metadata_filter(metadata))]

    def retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        return self._retrieve_context(query, n_results)
    
    async def _aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.client.as_retriever(
            search_kwargs={"k": n_results}
        )
        results = await retriever.ainvoke(query, filter=self.make_metadata_filter(metadata))
        logger.debug(f"Results: {results}")
        return [doc.page_content for doc in results]

    async def aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        """
        Retrieve the most relevant chunks of a document from the vector database.
        """
        return await self._aretrieve_context(query, n_results, metadata)
    
    def delete_document(self, document_id: str) -> None:
        self.client.delete(ids=[document_id])
