"""
Common utilities and models for the application.

This module contains shared models and utilities for the application.
"""

import warnings

# Import the models
from src.common.models import (
    Message,
    MessageTurn,
    ChatRequest,
    ChatResponse,
    Tool
)

# Import utility functions separately to avoid linter errors with typing
from src.common.models import messages_from_dict  # noqa

# Issue deprecation warnings
warnings.warn(
    "The common module structure has been reorganized. Please update your imports:\n"
    "- For config: from infrastructure.config import Config\n"
    "- For models: from src.common.models import X\n"
    "- For constants: from infrastructure.constants import X\n"
    "- For logging: from infrastructure.logging import logger",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "Message",
    "MessageTurn",
    "ChatRequest",
    "ChatResponse",
    "Tool",
    "messages_from_dict"
] 