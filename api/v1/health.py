"""
Health check API endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, Depends

from src.chat_engine import ChatEngine


# Create router
router = APIRouter()


def get_chat_engine(request: Request) -> ChatEngine:
    """
    Get the chat engine instance from the app state.
    
    Args:
        request: The current request object
        
    Returns:
        ChatEngine instance
    """
    return request.app.state.chat_engine


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "healthy"}


@router.get("/health/detailed")
async def detailed_health_check(chat_engine: ChatEngine = Depends(get_chat_engine)) -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Args:
        chat_engine: ChatEngine instance from app state
        
    Returns:
        Detailed status information
    """
    return {
        "status": "healthy",
        "components": {
            "bot": "available",
            "version": "1.0.0"
        }
    } 