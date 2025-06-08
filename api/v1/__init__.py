"""
API v1 module.
"""

from fastapi import APIRouter
from api.v1.chat import router as chat_router
from api.v1.health import router as health_router
from api.v1.rag import router as rag_router
from api.v1.experts import router as experts_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(chat_router, tags=["Chat"])
router.include_router(health_router, tags=["Health"])
router.include_router(rag_router, tags=["RAG"])
router.include_router(experts_router, tags=["Experts"])

__all__ = ["router"] 