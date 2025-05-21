from abc import ABC, abstractmethod

from typing import List


class BaseEmbedding(ABC):
    @abstractmethod
    def process(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def process_documents(self, documents: List[str]) -> List[List[float]]:
        pass
