from typing import Any, Dict, Optional
import os
import tempfile
import uuid

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
    temp_file_path = None
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate user_id and document_id
        user_id = "anonymous"
        document_id = str(uuid.uuid4())
        
        # Create a secure temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_file_path = temp_file.name
            
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()  # Ensure content is written to disk
        
        # Verify file exists and is readable
        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=500, detail="Failed to create temporary file")
        
        logger.info(f"Processing document: {file.filename} for user {user_id} with document_id {document_id}")
        
        # Process document with RAG bot
        rag_bot.process_document(temp_file_path, user_id, document_id)
        
        logger.info(f"Successfully processed document: {file.filename}")
        
        return {
            "success": True,
            "message": f"Document {file.filename} processed and indexed successfully",
            "document_id": document_id,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error processing document {file.filename if file.filename else 'unknown'}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {cleanup_error}")


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
        rag_bot: RAG bot expert instance
        current_user: Current authenticated user (optional)
        
    Returns:
        ChatResponse containing the bot's response
    """
    try:
        user_id = "anonymous"
        conversation_id = conversation_id or f"rag_{user_id}_{uuid.uuid4()}"
        
        logger.info(f"Processing RAG query for user {user_id}, conversation {conversation_id}")
        
        response = await rag_bot.aprocess(query, conversation_id, user_id)
        return response
    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}")
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
        rag_bot: RAG bot expert instance
        
    Returns:
        Dict containing success status and message
    """
    try:
        user_id = "anonymous"
        
        logger.info(f"Clearing RAG history for conversation {conversation_id} by user {user_id}")
        
        rag_bot.clear_history(conversation_id, user_id)
        return {
            "success": True,
            "message": f"History cleared for conversation {conversation_id}"
        }
    except Exception as e:
        logger.error(f"Error clearing RAG history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
