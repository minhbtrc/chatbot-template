"""
Chat API endpoints.
"""
from typing import Dict, Any
import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.v1.models import ChatRequest, ChatResponse, StreamingChatChunk
from api.v1.utils import get_chat_engine
from src.chat_engine import ChatEngine
from src.common.logging import logger


# Create router
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    chat_engine: ChatEngine = Depends(get_chat_engine)
) -> ChatResponse:
    """
    Chat endpoint for single user system.
    
    Args:
        request: Chat request containing input and conversation ID
        chat_engine: ChatEngine instance from the app state
        
    Returns:
        Response from the chat engine
    """
    conversation_id = request.conversation_id or ""
    
    logger.info(f"Received chat request for conversation {conversation_id}")
    logger.debug(f"User input: {request.input}")
    
    try:
        result = await chat_engine.process_message(
            user_input=request.input,
            conversation_id=conversation_id,
            user_id=""  # Single user system - no user ID needed
        )
        
        logger.info(f"Successfully processed chat request for conversation {result.conversation_id}")
        logger.debug(f"Chat engine response: {result.response}")
        
        # Return the response in the expected format for the API
        return ChatResponse(
            output=result.response,
            conversation_id=result.conversation_id,
            additional_kwargs=result.additional_kwargs
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise


@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest, 
    chat_engine: ChatEngine = Depends(get_chat_engine)
):
    """
    Streaming chat endpoint that returns Server-Sent Events (SSE).
    
    Args:
        request: Chat request containing input and conversation ID
        chat_engine: ChatEngine instance from the app state
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    conversation_id = request.conversation_id or ""
    
    logger.info(f"Received streaming chat request for conversation {conversation_id}")
    logger.debug(f"User input: {request.input}")
    
    async def generate_stream():
        """Generate the streaming response."""
        
        try:
            # Send start event
            start_chunk = StreamingChatChunk(
                type="start",
                conversation_id=conversation_id
            )
            yield f"data: {start_chunk.model_dump_json()}\n\n"
            
            # Stream the response chunks
            async for chunk in chat_engine.stream_process_message(
                user_input=request.input,
                conversation_id=conversation_id,
                user_id=""  # Single user system - no user ID needed
            ):
                if chunk:  # Only send non-empty chunks
                    chunk_data = StreamingChatChunk(
                        type="chunk",
                        content=chunk,
                        conversation_id=conversation_id
                    )
                    yield f"data: {chunk_data.model_dump_json()}\n\n"
                    
                    # Add a small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)
            
            # Send end event
            end_chunk = StreamingChatChunk(
                type="end",
                conversation_id=conversation_id
            )
            yield f"data: {end_chunk.model_dump_json()}\n\n"
            
            logger.info(f"Successfully streamed chat response for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error streaming chat response: {str(e)}")
            # Send error event
            error_chunk = StreamingChatChunk(
                type="error",
                error=str(e),
                conversation_id=conversation_id
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.post("/clear/{conversation_id}")
async def clear_history(
    conversation_id: str, 
    chat_engine: ChatEngine = Depends(get_chat_engine)
) -> Dict[str, Any]:
    """
    Clear the conversation history for a specific conversation ID.
    
    Args:
        conversation_id: ID of the conversation to clear
        chat_engine: ChatEngine instance from the app state
        
    Returns:
        Success message
    """
    logger.info(f"Received request to clear history for conversation {conversation_id}")
    
    try:
        chat_engine.clear_history(conversation_id=conversation_id, user_id="")
        logger.info(f"Successfully cleared history for conversation {conversation_id}")
        
        return {
            "status": "success", 
            "message": f"History for conversation {conversation_id} cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing history for conversation {conversation_id}: {str(e)}")
        raise
