"""
Chat API endpoints.
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict, Any

from api.v1.models import ChatRequest, ChatResponse
from src.chat_engine import ChatEngine
from src.common.logging import logger


# Create router
router = APIRouter()


def get_chat_engine(request: Request) -> ChatEngine:
    """
    Get the chat engine instance from the app state.
    
    Args:
        request: The current request object
        
    Returns:
        Bot instance
    """
    return request.app.state.chat_engine


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, chat_engine: ChatEngine = Depends(get_chat_engine)) -> ChatResponse:
    """
    Chat endpoint to process messages.
    
    Args:
        request: Chat request containing input and conversation ID
        chat_engine: ChatEngine instance from the app state
        
    Returns:
        Response from the chat engine
    """
    logger.info(f"Received chat request for conversation {request.conversation_id}")
    logger.debug(f"User input: {request.input}")
    
    try:
        result = await chat_engine.process_message(
            user_input=request.input,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"Successfully processed chat request for conversation {request.conversation_id}")
        logger.debug(f"Chat engine response: {result.response}")
        
        # Return the response in the expected format for the API
        return ChatResponse(
            output=result.response,
            conversation_id=result.conversation_id,
            additional_kwargs=result.additional_kwargs
        )
    except Exception as e:
        logger.error(f"Error processing chat request for conversation {request.conversation_id}: {str(e)}")
        raise


@router.post("/clear/{conversation_id}")
async def clear_history(conversation_id: str, chat_engine: ChatEngine = Depends(get_chat_engine)) -> Dict[str, Any]:
    """
    Clear the conversation history for a specific conversation ID.
    
    Args:
        conversation_id: ID of the conversation to clear
        bot: Bot instance from the app state
        
    Returns:
        Success message
    """
    logger.info(f"Received request to clear history for conversation {conversation_id}")
    
    try:
        chat_engine.clear_history(conversation_id=conversation_id)
        logger.info(f"Successfully cleared history for conversation {conversation_id}")
        
        return {
            "status": "success", 
            "message": f"History for conversation {conversation_id} cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing history for conversation {conversation_id}: {str(e)}")
        raise
