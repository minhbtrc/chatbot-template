"""FastAPI application for the chatbot."""
from typing import cast

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.common.config import Config
from src.bot import Bot
from dependency_injector import update_injector_with_config, get_instance
from api.middleware.error_handler import add_error_handling
from api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for setup and teardown."""
    # Startup: create bot instance with dependencies
    config = Config()
    update_injector_with_config(config)
    
    # Create bot with the brain and memory
    bot = cast(Bot, get_instance(Bot))
    
    app.state.bot = bot
    
    yield
    
    # Shutdown: close resources
    # Add cleanup logic here if needed


async def root_endpoint():
    """Root endpoint handler for API documentation redirect."""
    return {"message": "Welcome to the Chatbot API. Visit /docs for API documentation."}


def create_app() -> FastAPI:
    """Create the FastAPI application.
    
    Returns:
        FastAPI application.
    """
    
    app = FastAPI(
        title="LangChain Chatbot API",
        description="API for the LangChain chatbot",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add error handling middleware
    add_error_handling(app)
    
    # Include API version routers
    app.include_router(v1_router, prefix="/api")
    
    # Add root endpoint for API documentation redirect
    app.get("/", include_in_schema=False)(root_endpoint)
    
    return app 