from injector import inject

from src.common.config import Config
from src.base.components.embeddings.base import BaseEmbedding as EmbeddingsInterface
from .base import BaseVectorDatabase
from .variants.chromadb import ChromaVectorDatabase

@inject
def create_vector_database(config: Config, embeddings: EmbeddingsInterface) -> BaseVectorDatabase:
    """
    Create a vector database based on the type.
    """
    vector_database_type = config.vector_database_type.upper() if config.vector_database_type else None
    if vector_database_type == "CHROMA":
        return ChromaVectorDatabase(config, embeddings)
    else:
        raise ValueError(f"Invalid vector database type: {vector_database_type}")
