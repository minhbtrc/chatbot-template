from typing import Any, Dict

from fastapi import APIRouter, Request


router = APIRouter(tags=["RAG"])


@router.post("/document")
async def add_document(request: Request) -> Dict[str, Any]:
    """
    Add a document to the RAG index.
    """
    return {"status": "healthy"}
