"""
Health check API endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, Depends

from core.bot import Bot


# Create router
router = APIRouter()


def get_bot(request: Request) -> Bot:
    """
    Get the bot instance from the app state.
    
    Args:
        request: The current request object
        
    Returns:
        Bot instance
    """
    return request.app.state.bot


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "healthy"}


@router.get("/health/detailed")
async def detailed_health_check(bot: Bot = Depends(get_bot)) -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Args:
        bot: Bot instance from app state
        
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