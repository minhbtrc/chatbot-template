# Expert Switching System

This document describes the expert switching system that allows users to dynamically switch between different types of AI experts (QnA, RAG, etc.) in the chatbot application.

## Overview

The expert switching system provides a flexible architecture that allows:
- **Runtime Expert Switching**: Change expert types without restarting the application
- **Configuration-based Setup**: Set default expert type via environment variables
- **RESTful API Management**: Switch experts and get information via API endpoints
- **Backward Compatibility**: Existing chat functionality continues to work seamlessly

## Available Expert Types

### QnA Expert (`QNA`)
- **Purpose**: General question answering and conversational AI
- **Capabilities**: 
  - General knowledge queries
  - Conversational chat
  - Tool usage and function calling
  - Streaming responses
- **Use Cases**: General chatbot interactions, customer support, Q&A

### RAG Expert (`RAG`)
- **Purpose**: Retrieval-Augmented Generation for document-based queries
- **Capabilities**:
  - Document processing and indexing
  - Context retrieval from knowledge base
  - Document-based question answering
  - Streaming responses
- **Use Cases**: Knowledge base queries, document search, research assistance

## Configuration

### Environment Variables

Set the default expert type using the `EXPERT_TYPE` environment variable:

```bash
# Use QnA expert (default)
EXPERT_TYPE=QNA
c
# Use RAG expert
EXPERT_TYPE=RAG
```

### Configuration File

You can also set the expert type in your configuration:

```python
from src.common.config import Config

config = Config(expert_type="RAG")
```

## API Endpoints

### Get Current Expert Information

**GET** `/api/v1/experts/current`

Returns information about the currently active expert.

**Response:**
```json
{
  "current_expert": "QNA",
  "expert_info": {
    "expert_type": "QnaExpert"
  },
  "available_experts": ["QNA", "RAG"]
}
```

### Get Available Experts

**GET** `/api/v1/experts/available`

Returns information about all available expert types.

**Response:**
```json
{
  "available_experts": ["QNA", "RAG"],
  "expert_details": {
    "QNA": {
      "name": "QNA Expert",
      "description": "Question and Answer expert for general conversational AI",
      "capabilities": "General knowledge, conversation, tool usage"
    },
    "RAG": {
      "name": "RAG Expert",
      "description": "Retrieval-Augmented Generation expert for document-based Q&A",
      "capabilities": "Document processing, context retrieval, knowledge base queries"
    }
  },
  "total_count": 2
}
```

### Switch Expert Type

**POST** `/api/v1/experts/switch`

Switch to a different expert type.

**Request Body:**
```json
{
  "expert_type": "RAG"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully switched from QNA to RAG",
  "previous_expert": "QNA",
  "current_expert": "RAG"
}
```

### Get Expert Type Information

**GET** `/api/v1/experts/{expert_type}/info`

Get detailed information about a specific expert type.

**Response:**
```json
{
  "expert_type": "RAG",
  "info": {
    "name": "RAG Expert",
    "description": "Retrieval-Augmented Generation expert for document-based Q&A",
    "capabilities": "Document processing, context retrieval, knowledge base queries"
  },
  "supported_operations": [
    "process_message",
    "stream_message",
    "clear_history"
  ]
}
```

## Usage Examples

### Using cURL

```bash
# Get current expert info
curl -X GET "http://localhost:8080/api/v1/experts/current"

# Switch to RAG expert
curl -X POST "http://localhost:8080/api/v1/experts/switch" \
  -H "Content-Type: application/json" \
  -d '{"expert_type": "RAG"}'

# Get available experts
curl -X GET "http://localhost:8080/api/v1/experts/available"
```

### Using Python

```python
import requests

base_url = "http://localhost:8080/api/v1"

# Get current expert
response = requests.get(f"{base_url}/experts/current")
current_info = response.json()
print(f"Current expert: {current_info['current_expert']}")

# Switch to RAG expert
switch_response = requests.post(
    f"{base_url}/experts/switch",
    json={"expert_type": "RAG"}
)
print(f"Switch result: {switch_response.json()['message']}")

# Chat with the new expert
chat_response = requests.post(
    f"{base_url}/chat",
    json={
        "input": "What can you help me with?",
        "conversation_id": "test-conversation"
    }
)
print(f"Response: {chat_response.json()['output']}")
```

## Architecture

### Expert Factory

The `src/experts/factory.py` module provides:
- `create_expert()`: Creates expert instances based on configuration
- `get_available_expert_types()`: Returns list of available expert types
- `get_expert_info()`: Returns information about specific expert types

### Chat Engine Integration

The `ChatEngine` class manages expert switching:
- Maintains references to all expert instances
- Switches between experts based on configuration
- Provides unified interface for chat operations

### Base Expert Interface

All experts implement the `BaseExpert` interface:
- `process()`: Synchronous message processing
- `aprocess()`: Asynchronous message processing
- `stream_call()`: Synchronous streaming
- `astream_call()`: Asynchronous streaming
- `clear_history()`: Clear conversation history

## Error Handling

The system provides comprehensive error handling:

- **Invalid Expert Type**: Returns 400 Bad Request with available types
- **Expert Not Found**: Returns 404 Not Found for unknown expert types
- **Switch Failures**: Rolls back to previous expert on failure
- **API Errors**: Returns 500 Internal Server Error with error details

## Backward Compatibility

The expert switching system maintains full backward compatibility:
- Existing chat endpoints continue to work unchanged
- Default expert type is QnA if not specified
- All streaming functionality is preserved
- Memory and conversation management remains consistent

## Adding New Expert Types

To add a new expert type:

1. **Create Expert Class**: Implement `BaseExpert` interface
2. **Update Factory**: Add expert creation logic to `create_expert()`
3. **Update Info**: Add expert information to `get_expert_info()`
4. **Update Lists**: Add expert type to `get_available_expert_types()`
5. **Update Injection**: Add expert binding to dependency injection

Example:
```python
# In src/experts/factory.py
def create_expert(...):
    # ... existing code ...
    elif expert_type == "NEWTYPE":
        return NewExpert(config=config, ...)
    # ... rest of code ...

def get_available_expert_types():
    return ["QNA", "RAG", "NEWTYPE"]
```

## Testing

Run the factory function tests:
```bash
python test_api_experts.py
```

Test the API endpoints:
```bash
# Start the server
python -m uvicorn api.app:create_app --reload --port 8080

# Test endpoints
curl -X GET "http://localhost:8080/api/v1/experts/available"
```

## Troubleshooting

### Common Issues

1. **Expert Switch Fails**: Check that all required dependencies are properly injected
2. **API Returns 500**: Verify expert type is properly configured
3. **Memory Issues**: Ensure memory interface is compatible with all expert types
4. **Streaming Problems**: Check that expert implements streaming methods

### Logging

Enable debug logging to troubleshoot issues:
```bash
LOG_LEVEL=DEBUG python -m uvicorn api.app:create_app --reload
```

The system logs expert creation, switching, and API operations for debugging. 