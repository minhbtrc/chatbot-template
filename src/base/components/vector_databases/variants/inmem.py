from langchain_core.vectorstores import InMemoryVectorStore

from src.base.components.vector_databases.base import BaseVectorDatabase
from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface
from src.common.config import Config


class InMemoryVectorDatabase(BaseVectorDatabase):
    def __init__(self, config: Config, embeddings: EmbeddingsInterface):
        super().__init__(embeddings)
        self.config = config
        self.client = InMemoryVectorStore(embedding=self.embeddings.embeddings)
