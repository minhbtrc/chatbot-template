"""
Main FastAPI application module for the chatbot.
This entry point configures the FastAPI app with routes for the chatbot.
"""

import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api import create_app
from src.common.config import Config

# Load environment variables
load_dotenv()

# Create the FastAPI app
app = create_app()

# Configure CORS
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
    port = int(os.getenv("PORT", "8080"))
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=port)
