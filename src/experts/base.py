from abc import abstractmethod

from injector import inject

from src.common.config import Config
from src.common.schemas import ChatResponse


class BaseExpert:
    @inject
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def process(self, query: str, conversation_id: str) -> ChatResponse:
        pass

    @abstractmethod
    async def aprocess(self, query: str, conversation_id: str) -> ChatResponse:
        pass

    @abstractmethod
    def clear_history(self, conversation_id: str) -> None:
        pass
