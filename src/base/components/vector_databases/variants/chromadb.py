from typing import List, Any

from injector import inject
import chromadb

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
        self.client = chromadb.PersistentClient(path=config.vector_database_chroma_path)
        self.collection = self.client.get_or_create_collection(name="default")
        self.embeddings = embeddings

    def _index_documents(self, documents_embeddings: List[Any]) -> None:
        self.collection.add(embeddings=documents_embeddings, ids=[f"id{i}" for i in range(len(documents_embeddings))])
    
    def _retrieve_context(self, query_embedding: Any, n_results: int = 10) -> List[str]:
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results, include=["documents"])
        return results["documents"][0]

    def delete_document(self, document: str) -> None:
        self.collection.delete(ids=[document])
