"""FastAPI application for the chatbot."""
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings, Settings
from api.models import ChatRequest, ChatResponse
from api.middleware.error_handler import add_error_handling


def create_app() -> FastAPI:
    """Create the FastAPI application.
    
    Returns:
        FastAPI application.
    """
    
    app = FastAPI(
        title="LangChain Chatbot API",
        description="API for the LangChain chatbot",
        version="1.0.0",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add error handling middleware
    add_error_handling(app)
    
    # Define routes using Router objects to avoid linter warnings
    router = APIRouter()
    
    @router.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest, settings: Settings = Depends(get_settings)):
        """Process a chat message.
        
        Args:
            request: Chat request containing user message and conversation ID.
            settings: Application settings.
            
        Returns:
            AI response.
        """
        conversation_id = request.conversation_id or "default"
        
        # Use settings if needed
        _ = settings.model_type  # Example access to ensure settings is used
        
        response = await app.state.chat_manager.process_message(
            user_input=request.input,
            conversation_id=conversation_id
        )
        
        return ChatResponse(
            output=response,
            conversation_id=conversation_id
        )
    
    @router.post("/clear/{conversation_id}")
    async def clear_history_endpoint(conversation_id: str):
        """Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation.
            
        Returns:
            Status message.
        """
        app.state.chat_manager.clear_history(conversation_id)
        return {
            "status": "success",
            "message": f"History for conversation {conversation_id} cleared"
        }
    
    @router.get("/health")
    async def health_check_endpoint():
        """Health check endpoint.
        
        Returns:
            Status message.
        """
        return {"status": "healthy"}
    
    # Include the router in the app
    app.include_router(router)
    
    return app 