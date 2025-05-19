# API Documentation

This document describes the API endpoints and usage.

## Base URL

All API endpoints are prefixed with `/api/v1/`.

## Authentication

Authentication is currently implemented through environment variables. For production use, you should add proper authentication middleware.

**Recommended Authentication Methods:**
- OAuth2 with JWT tokens
- API Keys in Authorization header
- Session-based authentication for web applications

## Configuration

The API can be configured through environment variables:

```bash
# Core Configuration
MODEL_TYPE=AZUREOPENAI  # Options: OPENAI, LLAMA, AZUREOPENAI, VERTEX

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
BASE_MODEL_NAME=gpt-3.5-turbo

# Azure OpenAI Configuration
AZURE_API_KEY=your_azure_openai_key
AZURE_API_VERSION=2023-05-15
AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYMENT_NAME=your_deployment_name

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/chatbot
MONGO_DATABASE=langchain_bot
MONGO_COLLECTION=chatbot

# Server Configuration
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## Endpoints

### Chat

#### Send a message

```http
POST /api/v1/chat
Content-Type: application/json

{
  "input": "Hello, how are you?",
  "conversation_id": "optional-custom-id"
}
```

Sends a message to the chatbot and gets a response.

**Request Body:**
- `input` (string, required): The message to send
- `conversation_id` (string, optional): ID for the conversation

**Response:** `200 OK`
```json
{
  "output": "I'm doing well, thank you for asking! How can I assist you today?",
  "conversation_id": "conversation-id",
  "additional_kwargs": {}
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input format
- `500 Internal Server Error` - Server-side processing error
- `503 Service Unavailable` - LLM service error

#### Get conversation history

```
GET /api/v1/chat/history/{conversation_id}
```

Retrieves the conversation history for a specific conversation.

**Parameters:**
- `conversation_id` (path) - ID of the conversation to retrieve

**Response:** `200 OK`

```json
{
  "history": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you for asking! How can I assist you today?"
    }
  ],
  "conversation_id": "conversation-id"
}
```

**Error Responses:**
- `404 Not Found` - Conversation not found
- `500 Internal Server Error` - Server-side error

#### Clear conversation history

```http
POST /api/v1/clear/{conversation_id}
```

Clears the conversation history for a specific conversation.

**Parameters:**
- `conversation_id` (path) - ID of the conversation to clear

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "History for conversation {conversation_id} cleared"
}
```

**Error Responses:**
- `404 Not Found` - Conversation not found
- `500 Internal Server Error` - Server-side error

### Health Check

```http
GET /api/v1/health
```

Checks the health status of the API and its components.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "components": {
    "llm": "connected",
    "memory": "connected",
    "tools": "available"
  }
}
```

## Error Handling

The API uses a standardized error response format:

```json
{
  "error": {
    "type": "ErrorType",
    "message": "Human readable error message",
    "code": "error_code",
    "details": {
      // Additional error details if available
    }
  }
}
```

### Common Error Types

1. **ValidationError**
   - Status: 400
   - Occurs when request validation fails
   - Includes field-specific validation errors

2. **AuthenticationError**
   - Status: 401
   - Occurs when authentication fails
   - May include retry information

3. **AuthorizationError**
   - Status: 403
   - Occurs when user lacks required permissions

4. **ResourceNotFoundError**
   - Status: 404
   - Occurs when requested resource doesn't exist

5. **RateLimitError**
   - Status: 429
   - Includes `retry_after` field
   - Occurs when rate limits are exceeded

6. **LLMServiceError**
   - Status: 503
   - Occurs when LLM service is unavailable
   - May include service-specific error details

7. **InternalServerError**
   - Status: 500
   - Occurs for unexpected server errors
   - Includes error tracking ID

### Error Response Examples

#### Validation Error
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input format",
    "code": "validation_error",
    "details": {
      "field": "input",
      "error": "Field cannot be empty"
    }
  }
}
```

#### Rate Limit Error
```json
{
  "error": {
    "type": "RateLimitError",
    "message": "Too many requests",
    "code": "rate_limit_error",
    "details": {
      "retry_after": 60,
      "limit": 100,
      "remaining": 0
    }
  }
}
```

#### LLM Service Error
```json
{
  "error": {
    "type": "LLMServiceError",
    "message": "LLM service unavailable",
    "code": "llm_service_error",
    "details": {
      "service": "openai",
      "error_code": "service_unavailable",
      "retry_after": 30
    }
  }
}
```

## Logging

The API includes comprehensive logging for debugging and monitoring:

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General operational information
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

### Log Format

```
%(asctime)s [%(levelname)s] %(name)s: %(message)s
```

### Log Categories

1. **Request Logging**
   - Request method and path
   - Request headers
   - Request body (if applicable)
   - Response status
   - Processing time

2. **Error Logging**
   - Error type and message
   - Stack trace
   - Request context
   - Error tracking ID

3. **Performance Logging**
   - Response time
   - Resource usage
   - LLM call duration
   - Memory operations

4. **Security Logging**
   - Authentication attempts
   - Authorization failures
   - Rate limit hits
   - Suspicious activities

## Best Practices

1. **Error Handling**
   - Always check response status codes
   - Handle rate limits appropriately
   - Implement retry logic for transient errors
   - Log errors with sufficient context

2. **Rate Limiting**
   - Respect rate limits
   - Implement exponential backoff
   - Cache responses when appropriate
   - Monitor usage patterns

3. **Security**
   - Use HTTPS
   - Implement proper authentication
   - Validate all inputs
   - Sanitize outputs
   - Monitor for abuse

4. **Performance**
   - Use connection pooling
   - Implement caching
   - Monitor response times
   - Optimize payload sizes

## Integration Examples

### Curl

```bash
# Send a message
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, how are you?", "conversation_id": "test-conversation"}'

# Get conversation history
curl -X GET http://localhost:8080/api/v1/chat/history/test-conversation

# Clear conversation history
curl -X POST http://localhost:8080/api/v1/clear/test-conversation

# Health check
curl -X GET http://localhost:8080/api/v1/health
```

### Python

```python
import requests
import json

API_BASE_URL = "http://localhost:8080/api/v1"

def send_message(message, conversation_id=None):
    url = f"{API_BASE_URL}/chat"
    payload = {
        "input": message
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
        
    response = requests.post(url, json=payload)
    return response.json()

def get_history(conversation_id):
    url = f"{API_BASE_URL}/chat/history/{conversation_id}"
    response = requests.get(url)
    return response.json()

def clear_history(conversation_id):
    url = f"{API_BASE_URL}/clear/{conversation_id}"
    response = requests.post(url)
    return response.json()

# Example usage
response = send_message("Hello, how are you?", "my-conversation")
print(response)

history = get_history("my-conversation")
print(history)
```

### JavaScript

```javascript
const API_BASE_URL = 'http://localhost:8080/api/v1';

async function sendMessage(message, conversationId = null) {
  const payload = {
    input: message
  };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }
  
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  
  return response.json();
}

async function getHistory(conversationId) {
  const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`);
  return response.json();
}

async function clearHistory(conversationId) {
  const response = await fetch(`${API_BASE_URL}/clear/${conversationId}`, {
    method: 'POST'
  });
  return response.json();
}

// Example usage
sendMessage('Hello, how are you?', 'my-conversation')
  .then(response => console.log(response));
```

## Rate Limiting

Rate limiting is not currently implemented. For production use, you should add rate limiting middleware to prevent abuse.

**Recommended Implementation:**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
from typing import Dict, List

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: FastAPI, 
        rate_limit_per_minute: int = 60,
        burst_limit: int = 5
    ):
        super().__init__(app)
        self.rate_limit_per_minute = rate_limit_per_minute
        self.burst_limit = burst_limit
        self.request_records: Dict[str, List[float]] = {}
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limit
        current_time = time.time()
        if client_ip in self.request_records:
            # Remove timestamps older than 1 minute
            self.request_records[client_ip] = [
                timestamp for timestamp in self.request_records[client_ip]
                if current_time - timestamp < 60
            ]
            
            # Check if burst limit exceeded
            if len(self.request_records[client_ip]) >= self.burst_limit:
                time_diff = current_time - self.request_records[client_ip][0]
                if time_diff < 1.0:  # Less than 1 second
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please slow down."
                    )
            
            # Check if rate limit exceeded
            if len(self.request_records[client_ip]) >= self.rate_limit_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
                
            # Add current timestamp
            self.request_records[client_ip].append(current_time)
        else:
            # Initialize records for this IP
            self.request_records[client_ip] = [current_time]
            
        # Process the request
        return await call_next(request)

# In your main.py:
app = FastAPI()
app.add_middleware(RateLimitMiddleware)
```

## Versioning

The API is versioned through the URL path. The current version is `v1`.

When introducing breaking changes, a new version endpoint should be created (e.g., `/api/v2/`) while maintaining backward compatibility with existing clients.

## Command-Line Interface

For direct testing without the API, you can use the CLI:

```bash
# Basic usage
python cli.py

# Specify the model
python cli.py --model openai
python cli.py --model llama
python cli.py --model azureopenai

# Specify a conversation ID
python cli.py --conversation-id my_session_123
```

Exit the CLI by typing 'exit', 'quit', or pressing Ctrl+C.

## Extending the API

To add new endpoints, create a new router file in the `api/v1/` directory:

```python
# api/v1/custom.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

# Define request and response models
class CustomRequest(BaseModel):
    parameter: str
    
class CustomResponse(BaseModel):
    result: str
    status: str

# Create router
router = APIRouter(tags=["custom"])

@router.post("/custom-endpoint", response_model=CustomResponse)
async def custom_endpoint(request: CustomRequest):
    """
    Custom endpoint description.
    
    This endpoint does something custom.
    """
    try:
        # Implementation logic
        result = f"Processed: {request.parameter}"
        return CustomResponse(result=result, status="success")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Custom processing error: {str(e)}"
        )
```

Then register the router in `api/__init__.py`:

```python
from fastapi import FastAPI
from api.v1 import chat, health, custom

def create_app():
    app = FastAPI(
        title="LLM Backend API",
        description="API for interacting with LLM-powered services",
        version="1.0.0"
    )
    
    # Register routers
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(custom.router, prefix="/api/v1")
    
    return app
``` 