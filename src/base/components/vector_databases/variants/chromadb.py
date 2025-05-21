from typing import List

from injector import inject
import chromadb

from src.common.config import Config
from src.base.components.vector_databases.base import BaseVectorDatabase


class ChromaVectorDatabase(BaseVectorDatabase):
    @inject
    def __init__(self, config: Config):
        self.config = config
        if not config.vector_database_chroma_path:
            raise ValueError("Vector database path is not set")
        self.client = chromadb.PersistentClient(path=config.vector_database_chroma_path)
        self.collection = self.client.get_or_create_collection(name="default")

    def index_documents(self, documents: List[str]) -> None:
        self.collection.add(documents=documents, ids=[f"id{i}" for i in range(len(documents))])

    def retrieve_context(self, query: str, n_results: int = 10) -> List[str]:
        results = self.collection.query(query_texts=[query], n_results=n_results, include=["documents"])
        return results["documents"][0]

    def delete_document(self, document: str) -> None:
        self.collection.delete(ids=[document])
