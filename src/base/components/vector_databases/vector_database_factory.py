from src.common.config import Config
from .base import BaseVectorDatabase
from .variants.chromadb import ChromaVectorDatabase


def create_vector_database(config: Config) -> BaseVectorDatabase:
    """
    Create a vector database based on the type.
    """
    if config.vector_database_type and config.vector_database_type.upper() == "CHROMA":
        return ChromaVectorDatabase(config)
    else:
        raise ValueError(f"Invalid vector database type: {config.vector_database_type}")
