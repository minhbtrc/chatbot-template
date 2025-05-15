"""
API middleware module.

This module contains middleware components for the API.
"""

from api.middleware.error_handler import add_error_handling, ErrorHandlingMiddleware

__all__ = ["add_error_handling", "ErrorHandlingMiddleware"] 