from typing import List

from injector import inject
from pydantic import SecretStr
from langchain_openai import OpenAIEmbeddings

from src.base.components.embeddings.base import BaseEmbedding
from src.common.config import Config

class OpenAIEmbedding(BaseEmbedding):
    @inject
    def __init__(self, config: Config):
        if not config.openai_embedding_model:
            raise ValueError("OpenAI embedding model is not set")
        if not config.openai_api_key:
            raise ValueError("OpenAI API key is not set")
        self.embeddings = OpenAIEmbeddings(model=config.openai_embedding_model, api_key=SecretStr(config.openai_api_key))

    def process(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def process_documents(self, documents: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(documents)
    
    async def aprocess_documents(self, documents: List[str]) -> List[List[float]]:
        return await self.embeddings.aembed_documents(documents)
