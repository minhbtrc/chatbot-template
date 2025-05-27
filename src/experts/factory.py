from src.common.config import Config
from src.base.components import EmbeddingInterface, VectorDatabaseInterface, MemoryInterface, ToolProvider
from src.base.brains import BrainInterface
from src.experts.base import BaseExpert
from src.experts.rag_bot.expert import RAGBotExpert
from src.experts.qna.expert import QnaExpert


def create_expert(config: Config, embedding: EmbeddingInterface, vector_database: VectorDatabaseInterface, memory: MemoryInterface, brain: BrainInterface, tool_provider: ToolProvider) -> BaseExpert:
    expert_type = config.expert_type.upper() if config.expert_type else None
    if expert_type == "RAG":
        return RAGBotExpert(config=config, embedding=embedding, vector_database=vector_database, memory=memory, brain=brain)
    elif expert_type == "QNA":
        return QnaExpert(config=config, brain=brain, memory=memory, tool_provider=tool_provider)
    else:
        raise ValueError(f"Expert type {expert_type} not supported")