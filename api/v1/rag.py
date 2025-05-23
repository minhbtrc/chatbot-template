from typing import Any, Dict, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from src.experts.rag_bot.expert import RAGBotExpert
from src.common.schemas import ChatResponse
from src.common.logging import logger
from api.v1.utils import get_rag_bot


router = APIRouter(tags=["RAG"])


@router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    rag_bot: RAGBotExpert = Depends(get_rag_bot)
) -> Dict[str, Any]:
    """
    Process and index a document for RAG.
    
    Args:
        file: The document file to process
        
    Returns:
        Dict containing success status and message
    """
    try:
        # Save the uploaded file temporarily
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get RAG bot instance and process document
        rag_bot.process_document(file_path)
        
        return {
            "success": True,
            "message": f"Document {file.filename} processed and indexed successfully"
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query(
    query: str,
    conversation_id: Optional[str] = None,
    max_chunks: Optional[int] = 10,
    rag_bot: RAGBotExpert = Depends(get_rag_bot)
) -> ChatResponse:
    """
    Query the RAG bot with a question.
    
    Args:
        query: The question to ask
        conversation_id: Optional conversation ID for context
        max_chunks: Maximum number of context chunks to retrieve
        
    Returns:
        ChatResponse containing the bot's response
    """
    try:
        response = await rag_bot.aprocess(query, conversation_id or "default")
        return response
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-history")
async def clear_history(
    conversation_id: str,
    rag_bot: RAGBotExpert = Depends(get_rag_bot)
) -> Dict[str, Any]:
    """
    Clear the conversation history for a specific conversation.
    
    Args:
        conversation_id: ID of the conversation to clear
        
    Returns:
        Dict containing success status and message
    """
    try:
        rag_bot.clear_history(conversation_id)
        return {
            "success": True,
            "message": f"History cleared for conversation {conversation_id}"
        }
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
