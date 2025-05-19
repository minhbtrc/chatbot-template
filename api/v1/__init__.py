"""
API v1 module.
"""

from fastapi import APIRouter
from api.v1.chat import router as chat_router
from api.v1.health import router as health_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(chat_router, tags=["chat"])
router.include_router(health_router, tags=["health"])

__all__ = ["router"] 