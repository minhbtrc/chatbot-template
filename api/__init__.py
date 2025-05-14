"""API module for the chatbot application."""
from fastapi import FastAPI

from api.v1 import router as v1_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Chatbot API",
        description="API for interacting with the LangChain-powered chatbot",
        version="1.0.0",
    )
    
    # Include API version routes
    app.include_router(v1_router)
    
    # Add root endpoint for API documentation redirect
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Welcome to the Chatbot API. Visit /docs for API documentation."}
    
    return app 