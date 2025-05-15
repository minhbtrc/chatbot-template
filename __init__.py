# This file is intentionally left mostly empty to avoid circular imports
# Only import what's necessary for basic package initialization
"""
Chatbot Backend package.

This package contains the backend code for the chatbot application.
It provides a FastAPI application that exposes various endpoints for chatting.
"""

__version__ = "2.0.0"

# Expose key components for easier imports
from config import settings
from api import create_app

__all__ = ["settings", "create_app"]
