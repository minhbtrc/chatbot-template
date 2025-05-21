from src.common.config import Config
from .base import BaseVectorDatabase
from .variants.chromadb import ChromaVectorDatabase


def create_vector_database(config: Config) -> BaseVectorDatabase:
    """
    Create a vector database based on the type.
    """
    vector_database_type = config.vector_database_type.upper() if config.vector_database_type else None
    if vector_database_type == "CHROMA":
        return ChromaVectorDatabase(config)
    else:
        raise ValueError(f"Invalid vector database type: {vector_database_type}")
