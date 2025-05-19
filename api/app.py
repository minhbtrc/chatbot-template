"""FastAPI application for the chatbot."""
from typing import cast

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.chat_engine import ChatEngine
from src.common.config import Config
from src.config_injector import update_injector_with_config, get_instance
from api.middleware.error_handler import add_error_handling
from api.v1 import router as v1_router
from src.common.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for setup and teardown."""
    # Startup: create bot instance with dependencies
    logger.info("Starting application initialization")
    
    try:
        config = Config()
        logger.info(f"Configuration loaded with model type: {config.model_type}")
        
        update_injector_with_config(config)
        logger.debug("Dependency injection configured")
        
        # Create bot with the brain and memory
        chat_engine = cast(ChatEngine, get_instance(ChatEngine))
        logger.info("Chat engine initialized successfully")
        
        app.state.chat_engine = chat_engine
        logger.info("Application startup complete")
        
        yield
        
        # Shutdown: close resources
        logger.info("Starting application shutdown")
        if hasattr(app.state.chat_engine, 'close'):
            logger.debug("Closing chat engine resources")
            app.state.chat_engine.close()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during application lifecycle: {str(e)}")
        raise


async def root_endpoint():
    """Root endpoint handler for API documentation redirect."""
    return {"message": "Welcome to the Chatbot API. Visit /docs for API documentation."}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    logger.info("Creating FastAPI application")
    
    app = FastAPI(
        title="Chatbot API",
        description="API for interacting with the chatbot",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add error handling middleware
    add_error_handling(app)
    logger.debug("Error handling middleware added")
    
    # Include API routers
    app.include_router(v1_router, prefix="/api/v1")
    logger.debug("API routers configured")
    
    # Add root endpoint for API documentation redirect
    app.get("/", include_in_schema=False)(root_endpoint)
    
    logger.info("FastAPI application created successfully")
    return app 