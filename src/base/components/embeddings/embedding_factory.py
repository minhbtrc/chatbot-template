from common.config import Config
from .variants.azure_openai_embedding import OpenAIEmbedding
from .base import BaseEmbedding


def create_embedding(config: Config) -> BaseEmbedding:
    if config.embedding_type == "openai":
        return OpenAIEmbedding(config)
    else:
        raise ValueError(f"Embedding type {config.embedding_type} not supported")
classmethod