"""
Health check API endpoints.
"""

from typing import Dict

from fastapi import APIRouter

# Create router
router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status message
    """
    return {"status": "healthy"} 