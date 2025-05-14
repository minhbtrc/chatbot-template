# Architecture Guide

This document provides a detailed overview of the LLM Backend Framework architecture.

## Overview

The architecture follows a modular Bot-Brain pattern with standardized interfaces for extensibility:

```
Bot → Brain → LLM Client → External LLM API
```

Components are organized into logical domains based on their responsibilities.

## Key Components

### Bot Layer

The Bot layer is responsible for:
- Handling user messages
- Managing conversation state
- Coordinating between reasoning (brain) and memory components

```python
# src/bot/bot.py
class Bot:
    def __init__(self, brain: BaseBrain, memory: Optional[BaseChatbotMemory] = None, tools: Optional[List[Any]] = None):
        # ...
    
    def call(self, sentence: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        # Process message using brain and memory
        # ...
```

### Reasoning Layer

The reasoning layer contains:

#### Brains

Brains encapsulate the reasoning logic and are responsible for:
- Processing user queries
- Generating responses using LLMs
- Utilizing tools when needed

```python
# src/reasoning/brains/base.py
class BaseBrain(ABC):
    @abstractmethod
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process the query and return a response."""
        pass
```

Current implementations:
- `OpenAIBrain`: Uses OpenAI models for reasoning
- `LlamaBrain`: Uses local LlamaCpp models

#### Chains

Chains implement specific reasoning flows:
- Retrieval chains for information lookups
- Specialized reasoning patterns

### LLM Clients

LLM Clients abstract the communication with language model providers:
- Standardized interface across providers
- Methods for chat, completion, and embeddings
- Provider-specific implementation details

```python
# src/llm_clients/base.py
class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Send a chat message to the LLM and get a response."""
        pass
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send a completion prompt to the LLM and get a response."""
        pass
    
    @abstractmethod
    def create_embedding(self, text: Union[str, List[str]], **kwargs: Any) -> List[List[float]]:
        """Create embeddings for the given text(s)."""
        pass
```

### Tools

Tools extend the capabilities of the system:
- Search capabilities
- Data processing
- External API integrations

```python
# src/tools/base.py
class BaseTool(ABC):
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the tool with the given input."""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the tool's parameters."""
        pass
```

### Memory Systems

Memory components store and retrieve conversation history:
- In-memory implementations for testing
- MongoDB-based persistent storage

```python
# src/memory/base_memory.py
class BaseChatbotMemory(ABC):
    @abstractmethod
    def add_message(self, role: str, content: str, conversation_id: str) -> None:
        """Add a message to the conversation history."""
        pass
    
    @abstractmethod
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get the conversation history."""
        pass
```

## Flow of Operation

1. User message enters through API
2. Bot receives message and retrieves conversation history
3. Brain processes the message with context
4. Brain may use tools for enhanced capabilities
5. LLM Client communicates with external LLM provider
6. Response is returned to the user
7. Conversation is stored in memory

## Design Principles

1. **Single Responsibility Principle**: Each component has a clear, specific role
2. **Open/Closed Principle**: Extensions come through new implementations, not modifications
3. **Interface Segregation**: Clear, focused interfaces for each component type
4. **Dependency Inversion**: High-level components depend on abstractions, not details

## Directory Structure

```
├── api/                  # API layer with FastAPI
├── src/                  # Source code
│   ├── bot/              # Bot implementation
│   ├── reasoning/        # Reasoning components
│   │   ├── brains/       # LLM-powered reasoning
│   │   └── chains/       # Chain implementations
│   ├── memory/           # Conversation memory modules
│   ├── llm_clients/      # LLM service wrappers
│   ├── common/           # Shared utilities and models
│   ├── tools/            # Tools for agent capabilities
│   └── prompts/          # Prompt templates
├── tests/                # Test directory
└── infrastructure/       # Infrastructure concerns
```

## Configuration

The system is configured through a centralized Config class that handles:
- Environment variables
- Default values
- Type validation

```python
# infrastructure/config.py
class Config:
    def __init__(self):
        # Load configuration from environment variables
        # ...
``` 