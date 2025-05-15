"""
Main FastAPI application entry point for the chatbot backend.

This is the main entry point for running the application. It:
1. Loads environment variables
2. Creates the FastAPI app using the factory in api/app.py
3. Configures global middleware
4. Starts the server when run directly
"""

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api import create_app
from src.common.config import Config

# Load environment variables
load_dotenv()

# Create the FastAPI app using the factory function
app = create_app()

# Configure global CORS middleware
# This applies to all routes in the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if __name__ == "__main__":
    # Load config
    config = Config()
    
    # Get port from environment or config
    port = int(config.port)
    
    print(f"Starting server on port {port}...")
    print(f"API documentation available at http://localhost:{port}/docs")
    
    # Run the application with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
