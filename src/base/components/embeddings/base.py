from abc import ABC, abstractmethod

from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from src.common.config import Config


class BaseEmbedding(ABC):
    def __init__(self, config: Config):
        self.config = config
        self.embeddings: Embeddings

    @abstractmethod
    def process(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def process_documents(self, documents: List[Document]) -> List[List[float]]:
        pass

    @abstractmethod
    async def aprocess_documents(self, documents: List[Document]) -> List[List[float]]:
        pass
