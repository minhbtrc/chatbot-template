from fastapi import Request

from src.experts.rag_bot.expert import RAGBotExpert
from src.chat_engine import ChatEngine


def get_chat_engine(request: Request) -> ChatEngine:
    """
    Get the chat engine instance from the app state.
    
    Args:
        request: The current request object
        
    Returns:
        Bot instance
    """
    return request.app.state.chat_engine


def get_rag_bot(request: Request) -> RAGBotExpert:
    """
    Get the RAG bot instance from the app state.
    
    Args:
        request: The current request object
        
    Returns:
        RAG bot instance
    """
    return request.app.state.rag_bot
