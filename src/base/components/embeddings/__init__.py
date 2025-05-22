from .base import BaseEmbedding
from .embedding_factory import create_embedding
from .variants.azure_openai_embedding import AzureOpenAIEmbedding

__all__ = ["BaseEmbedding", "create_embedding", "AzureOpenAIEmbedding"]