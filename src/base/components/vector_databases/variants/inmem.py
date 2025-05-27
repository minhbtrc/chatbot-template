from typing import List, Dict, Any

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from loguru import logger

from src.base.components.vector_databases.base import BaseVectorDatabase
from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface
from src.common.config import Config


class InMemoryVectorDatabase(BaseVectorDatabase):
    def __init__(self, config: Config, embeddings: EmbeddingsInterface):
        super().__init__(embeddings)
        self.config = config
        self.vector_store = InMemoryVectorStore(embedding=self.embeddings.embeddings)

    def _index_documents(self, documents: List[Document]) -> List[str]:
        return self.vector_store.add_documents(documents)

    async def _aindex_documents(self, documents: List[Document]) -> List[str]:
        return await self.vector_store.aadd_documents(documents)

    def _retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": n_results}
        )
        return [doc.page_content for doc in retriever.invoke(query, filter=metadata)]
    
    async def _aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": n_results}
        )
        results = await retriever.ainvoke(query, filter=metadata)
        logger.info(f"Results: {results}")
        return [doc.page_content for doc in results]
    
    def delete_document(self, document: str) -> None:
        self.vector_store.delete(document)

