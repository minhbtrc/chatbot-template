# API Documentation

This document describes the API endpoints available in the LLM Backend Framework.

## Base URL

All API endpoints are prefixed with `/v1/` to support versioning.

## Authentication

Authentication is currently implemented through environment variables. For production use, you should add proper authentication middleware.

## Endpoints

### Chat Endpoint

Process a user message and get a response from the LLM.

**URL:** `/v1/chat`

**Method:** `POST`

**Request Body:**

```json
{
  "input": "Hello, how can you help me today?",
  "conversation_id": "unique-conversation-identifier"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `input` | string | The user's message |
| `conversation_id` | string | Unique identifier for the conversation |

**Response:**

```json
{
  "response": "I'm an AI assistant built with the LLM Backend Framework. I can answer questions, provide information, and help with various tasks. How can I assist you today?",
  "conversation_id": "unique-conversation-identifier"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The LLM's response |
| `conversation_id` | string | The same conversation ID that was provided |

**Example:**

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"input": "What can you tell me about machine learning?", "conversation_id": "user123-session456"}'
```

### Clear History Endpoint

Clear the conversation history for a specific conversation.

**URL:** `/v1/clear/{conversation_id}`

**Method:** `POST`

**URL Parameters:**

| Parameter | Description |
|-----------|-------------|
| `conversation_id` | The conversation ID to clear |

**Response:**

```json
{
  "status": "success",
  "message": "History for conversation user123-session456 cleared"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/v1/clear/user123-session456
```

### Health Check Endpoint

Check the health of the API.

**URL:** `/v1/health`

**Method:** `GET`

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**Example:**

```bash
curl http://localhost:8000/v1/health
```

## Error Handling

The API returns appropriate HTTP status codes for different types of errors:

- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

Error responses include a JSON body with more details:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {} // Optional additional information
}
```

## Rate Limiting

Currently, rate limiting is not implemented. For production use, consider adding rate limiting middleware.

## Command Line Interface

For testing and development purposes, a CLI interface is available that allows interacting with the chatbot without the API.

### Usage

```bash
# Basic usage
python cli.py

# Specify a model type
python cli.py --model llama

# Specify a custom conversation ID
python cli.py --conversation-id my_session_123
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model` | Model type to use (`openai` or `llama`) | `openai` |
| `--conversation-id` | Conversation ID for the session | `cli_session` |

Exit the CLI by typing 'exit', 'quit', or pressing Ctrl+C.

## Extending the API

To add new endpoints, create a new router file in the `api/v1/` directory:

```python
# api/v1/custom.py
from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()

@router.post("/custom-endpoint")
async def custom_endpoint(request_data: YourRequestModel) -> Dict[str, Any]:
    """
    Your custom endpoint.
    """
    # Implementation
    return {"result": "custom result"}
```

Then register the router in `api/__init__.py`:

```python
from api.v1 import chat, health, custom

def create_app():
    app = FastAPI()
    
    # Register routers
    app.include_router(chat.router, prefix="/v1")
    app.include_router(health.router, prefix="/v1")
    app.include_router(custom.router, prefix="/v1")
    
    return app
``` 