"""
Chat API endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any

from api.v1.models import ChatRequest, ChatResponse
from src.bot.bot import Bot
from src.reasoning.brains.brain_factory import create_brain
from src.memory.clients.mongodb_memory import MongoMemory
from src.common.config import Config


# Create router
router = APIRouter()

# Create the config
config = Config()

# Create a brain based on the config
brain = create_brain(config)

# Create the memory
memory = MongoMemory(config)

# Create bot instance
bot = Bot(
    brain=brain,
    memory=memory
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint to process messages.
    
    Args:
        request: Chat request containing input and conversation ID
        
    Returns:
        Response from the bot
    """
    result = bot.call(
        sentence=request.input,
        conversation_id=request.conversation_id
    )
    
    # Return the response in the expected format for the API
    return ChatResponse(
        output=result["response"],
        conversation_id=result["conversation_id"]
    )


@router.post("/clear/{conversation_id}")
async def clear_history(conversation_id: str) -> Dict[str, Any]:
    """
    Clear the conversation history for a specific conversation ID.
    
    Args:
        conversation_id: ID of the conversation to clear
        
    Returns:
        Success message
    """
    bot.reset_history(conversation_id=conversation_id)
    
    return {
        "status": "success", 
        "message": f"History for conversation {conversation_id} cleared"
    } 