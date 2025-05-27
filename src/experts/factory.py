"""
Expert factory for creating different types of experts.
"""

from src.common.config import Config
from src.base.components import EmbeddingInterface, VectorDatabaseInterface, MemoryInterface, ToolProvider
from src.base.brains import BrainInterface
from src.experts.base import BaseExpert
from src.experts.rag_bot.expert import RAGBotExpert
from src.experts.qna.expert import QnaExpert
from src.common.logging import logger


def create_expert(
    config: Config, 
    embedding: EmbeddingInterface, 
    vector_database: VectorDatabaseInterface, 
    memory: MemoryInterface, 
    brain: BrainInterface, 
    tool_provider: ToolProvider
) -> BaseExpert:
    """
    Create an expert instance based on the configuration.
    
    Args:
        config: Application configuration
        embedding: Embedding interface for vector operations
        vector_database: Vector database interface for document storage
        memory: Memory interface for conversation history
        brain: Brain interface for reasoning
        tool_provider: Tool provider for expert capabilities
        
    Returns:
        BaseExpert instance of the specified type
        
    Raises:
        ValueError: If the expert type is not supported
    """
    expert_type = config.expert_type.upper() if config.expert_type else "QNA"
    
    logger.info(f"Creating expert of type: {expert_type}")
    
    if expert_type == "RAG":
        logger.debug("Creating RAG expert with embedding and vector database")
        return RAGBotExpert(
            config=config, 
            embedding=embedding, 
            vector_database=vector_database, 
            memory=memory, 
            brain=brain
        )
    elif expert_type == "QNA":
        logger.debug("Creating QNA expert with brain and tools")
        return QnaExpert(
            config=config, 
            brain=brain, 
            memory=memory, 
            tool_provider=tool_provider
        )
    else:
        available_types = ["QNA", "RAG"]
        error_msg = f"Expert type '{expert_type}' not supported. Available types: {', '.join(available_types)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def get_available_expert_types() -> list[str]:
    """
    Get list of available expert types.
    
    Returns:
        List of available expert type names
    """
    return ["QNA", "RAG"]


def get_expert_info(expert_type: str) -> dict[str, str]:
    """
    Get information about a specific expert type.
    
    Args:
        expert_type: The type of expert to get info for
        
    Returns:
        Dictionary containing expert information
        
    Raises:
        ValueError: If the expert type is not supported
    """
    expert_type = expert_type.upper()
    
    expert_info_map = {
        "QNA": {
            "name": "QNA Expert",
            "description": "Question and Answer expert for general conversational AI",
            "capabilities": "General knowledge, conversation, tool usage"
        },
        "RAG": {
            "name": "RAG Expert", 
            "description": "Retrieval-Augmented Generation expert for document-based Q&A",
            "capabilities": "Document processing, context retrieval, knowledge base queries"
        }
    }
    
    if expert_type not in expert_info_map:
        available_types = list(expert_info_map.keys())
        raise ValueError(f"Expert type '{expert_type}' not supported. Available types: {', '.join(available_types)}")
    
    return expert_info_map[expert_type]