"""
Chat API endpoints.
"""

from fastapi import APIRouter, Depends, Request
from typing import Dict, Any

from api.v1.models import ChatRequest, ChatResponse
from src.bot import Bot


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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, bot: Bot = Depends(get_bot)) -> ChatResponse:
    """
    Chat endpoint to process messages.
    
    Args:
        request: Chat request containing input and conversation ID
        bot: Bot instance from the app state
        
    Returns:
        Response from the bot
    """
    result = bot.call(
        sentence=request.input,
        conversation_id=request.conversation_id
    )
    
    # Return the response in the expected format for the API
    return ChatResponse(
        output=result.response,
        conversation_id=result.conversation_id,
        additional_kwargs=result.additional_kwargs
    )


@router.post("/clear/{conversation_id}")
async def clear_history(conversation_id: str, bot: Bot = Depends(get_bot)) -> Dict[str, Any]:
    """
    Clear the conversation history for a specific conversation ID.
    
    Args:
        conversation_id: ID of the conversation to clear
        bot: Bot instance from the app state
        
    Returns:
        Success message
    """
    bot.reset_history(conversation_id=conversation_id)
    
    return {
        "status": "success", 
        "message": f"History for conversation {conversation_id} cleared"
    }
