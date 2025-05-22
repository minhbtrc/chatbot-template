from typing import List

from injector import inject
from pydantic import SecretStr
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document

from src.base.components.embeddings.base import BaseEmbedding
from src.common.config import Config


class AzureOpenAIEmbedding(BaseEmbedding):
    @inject
    def __init__(self, config: Config):
        super().__init__(config)
        if not config.azure_embedding_model_key:
            raise ValueError("Azure embedding model key is not set")
        if not config.azure_embedding_model_endpoint:
            raise ValueError("Azure embedding model endpoint is not set")
        if not config.azure_embedding_model_deployment:
            raise ValueError("Azure embedding model deployment is not set")
        
        self.embeddings = AzureOpenAIEmbeddings(
            api_key=SecretStr(config.azure_embedding_model_key),
            azure_endpoint=config.azure_embedding_model_endpoint,
            azure_deployment=config.azure_embedding_model_deployment,
            api_version=config.azure_embedding_model_version,
        )

    def process(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def process_documents(self, documents: List[Document]) -> List[List[float]]:
        return self.embeddings.embed_documents([doc.page_content for doc in documents])
    
    async def aprocess_documents(self, documents: List[Document]) -> List[List[float]]:
        return await self.embeddings.aembed_documents([doc.page_content for doc in documents])
