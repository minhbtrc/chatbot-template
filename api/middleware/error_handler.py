"""
Error handling middleware for FastAPI.

This middleware catches framework exceptions and converts them to appropriate HTTP responses.
"""

from typing import Dict, Any, Callable, Union, Awaitable

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.common.exceptions import FrameworkError, HTTP_STATUS_CODES
from src.common.logging import logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling custom exceptions."""
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Any]]
    ) -> Union[JSONResponse, Any]:
        """
        Process a request and handle any framework exceptions.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            Either a JSON response with error details or the regular response
        """
        try:
            # Log request details
            logger.debug(f"Processing request: {request.method} {request.url.path}")
            
            # Try to process the request normally
            response = await call_next(request)
            
            # Log successful response
            logger.debug(f"Request completed successfully: {request.method} {request.url.path}")
            return response
            
        except FrameworkError as e:
            # Get the appropriate status code for this exception type
            status_code = HTTP_STATUS_CODES.get(type(e), 500)
            
            # Log the error with detailed information
            logger.error(
                f"Framework error in {request.method} {request.url.path}: "
                f"Type: {type(e).__name__}, "
                f"Message: {str(e)}, "
                f"Status: {status_code}"
            )
            
            # Prepare the error response
            error_response: Dict[str, Any] = {
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "code": f"{type(e).__name__.lower()}_error"
                }
            }
            
            # Add additional fields if they exist
            if hasattr(e, "status_code") and e.status_code is not None:
                error_response["error"]["api_status_code"] = e.status_code
                logger.debug(f"API status code: {e.status_code}")
            
            if hasattr(e, "retry_after") and e.retry_after is not None:
                error_response["error"]["retry_after"] = e.retry_after
                logger.debug(f"Retry after: {e.retry_after}")
                
            if hasattr(e, "field") and e.field is not None:
                error_response["error"]["field"] = e.field
                logger.debug(f"Error field: {e.field}")
                
            if hasattr(e, "tool_name") and e.tool_name is not None:
                error_response["error"]["tool_name"] = e.tool_name
                logger.debug(f"Error tool: {e.tool_name}")
            
            # Return the error response
            return JSONResponse(
                status_code=status_code,
                content=error_response
            )
        except Exception as e:
            # Catch any other exceptions and return a generic 500 error
            logger.exception(
                f"Unhandled error in {request.method} {request.url.path}: "
                f"Type: {type(e).__name__}, "
                f"Message: {str(e)}"
            )
            
            error_response = {
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "code": "internal_server_error"
                }
            }
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )


def add_error_handling(app: FastAPI) -> None:
    """
    Add error handling middleware to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Adding error handling middleware")
    app.add_middleware(ErrorHandlingMiddleware)
    logger.debug("Error handling middleware added successfully")