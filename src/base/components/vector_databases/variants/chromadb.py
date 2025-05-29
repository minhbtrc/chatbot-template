from injector import inject
from langchain_chroma import Chroma

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
