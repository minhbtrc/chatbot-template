from typing import List, Dict, Any

from injector import inject
from langchain_chroma import Chroma
from langchain_core.documents import Document
from loguru import logger

from src.common.config import Config
from src.base.components.vector_databases.base import BaseVectorDatabase
from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface


class ChromaVectorDatabase(BaseVectorDatabase):
    @inject
    def __init__(self, config: Config, embeddings: EmbeddingsInterface):
        super().__init__(embeddings)
        self.config = config
        if not config.vector_database_chroma_path:
            raise ValueError("Vector database path is not set")
        self.client = Chroma(
            collection_name="default",
            persist_directory=config.vector_database_chroma_path,
            embedding_function=self.embeddings.embeddings
        )

    def _index_documents(self, documents: List[Document]) -> List[str]:
        return self.client.add_documents(documents=documents, ids=[f"id{i}" for i in range(len(documents))])

    async def _aindex_documents(self, documents: List[Document]) -> List[str]:
        return await self.client.aadd_documents(documents=documents, ids=[f"id{i}" for i in range(len(documents))])
    
    def _retrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.client.as_retriever(
            search_kwargs={"k": n_results}
        )
        return [doc.page_content for doc in retriever.invoke(query, filter=metadata)]
    
    async def _aretrieve_context(self, query: str, n_results: int = 10, metadata: Dict[str, Any] = {}) -> List[str]:
        logger.info(f"Retrieving context for query: {query}")
        logger.info(f"Metadata: {metadata}")
        retriever = self.client.as_retriever(
            search_kwargs={"k": n_results}
        )
        results = await retriever.ainvoke(query, filter=metadata)
        logger.info(f"Results: {results}")
        return [doc.page_content for doc in results]

    def delete_document(self, document: str) -> None:
        self.client.delete(ids=[document])
