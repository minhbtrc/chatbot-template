from fastapi import Request

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
