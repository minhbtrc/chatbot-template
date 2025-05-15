"""
Exceptions module containing all custom exceptions used in the framework.

This module defines a hierarchy of exceptions that can be raised by different
components of the framework. These exceptions are designed to be caught and
handled appropriately, especially in API endpoints.
"""

from typing import Optional

class FrameworkError(Exception):
    """Base class for all framework exceptions."""
    
    def __init__(self, message: str = "An error occurred in the framework"):
        self.message = message
        super().__init__(self.message)


# LLM Client exceptions
class LLMClientError(FrameworkError):
    """Base class for all LLM client exceptions."""
    
    def __init__(self, message: str = "An error occurred in the LLM client"):
        self.message = message
        super().__init__(self.message)


class ConnectionError(LLMClientError):
    """Raised when a connection to the LLM provider fails."""
    
    def __init__(self, message: str = "Failed to connect to the LLM provider"):
        self.message = message
        super().__init__(self.message)


class APIError(LLMClientError):
    """Raised when the LLM provider API returns an error."""
    
    def __init__(self, message: str = "The LLM provider API returned an error", status_code: Optional[int] = None, response: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class RateLimitError(LLMClientError):
    """Raised when the LLM provider rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded for the LLM provider", retry_after: Optional[int] = None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


# Brain exceptions
class BrainError(FrameworkError):
    """Base class for all brain exceptions."""
    
    def __init__(self, message: str = "An error occurred in the brain"):
        self.message = message
        super().__init__(self.message)


class ThinkingError(BrainError):
    """Raised when the brain's thinking process fails."""
    
    def __init__(self, message: str = "Failed to process the query"):
        self.message = message
        super().__init__(self.message)


class ToolExecutionError(BrainError):
    """Raised when a tool execution fails."""
    
    def __init__(self, message: str = "Failed to execute tool", tool_name: Optional[str] = None):
        self.message = message
        self.tool_name = tool_name
        super().__init__(self.message)


# Memory exceptions
class MemoryError(FrameworkError):
    """Base class for all memory exceptions."""
    
    def __init__(self, message: str = "An error occurred in the memory system"):
        self.message = message
        super().__init__(self.message)


class StorageError(MemoryError):
    """Raised when storing data in memory fails."""
    
    def __init__(self, message: str = "Failed to store data in memory"):
        self.message = message
        super().__init__(self.message)


class RetrievalError(MemoryError):
    """Raised when retrieving data from src.components.memory fails."""
    
    def __init__(self, message: str = "Failed to retrieve data from src.components.memory"):
        self.message = message
        super().__init__(self.message)


# Tool exceptions
class ToolError(FrameworkError):
    """Base class for all tool exceptions."""
    
    def __init__(self, message: str = "An error occurred in a tool"):
        self.message = message
        super().__init__(self.message)


# Configuration exceptions
class ConfigurationError(FrameworkError):
    """Raised when there is an issue with the configuration."""
    
    def __init__(self, message: str = "Invalid configuration"):
        self.message = message
        super().__init__(self.message)


class ValidationError(ConfigurationError):
    """Raised when configuration validation fails."""
    
    def __init__(self, message: str = "Configuration validation failed", field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


# Mapping of exceptions to HTTP status codes
HTTP_STATUS_CODES = {
    LLMClientError: 503,  # Service Unavailable
    ConnectionError: 503,  # Service Unavailable
    APIError: 503,  # Service Unavailable
    RateLimitError: 429,  # Too Many Requests
    BrainError: 500,  # Internal Server Error
    ThinkingError: 500,  # Internal Server Error
    ToolExecutionError: 500,  # Internal Server Error
    MemoryError: 500,  # Internal Server Error
    StorageError: 500,  # Internal Server Error
    RetrievalError: 500,  # Internal Server Error
    ToolError: 500,  # Internal Server Error
    ConfigurationError: 500,  # Internal Server Error
    ValidationError: 400,  # Bad Request
    FrameworkError: 500,  # Internal Server Error
}