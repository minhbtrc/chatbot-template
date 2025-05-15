# Folder Structure

This document describes the folder structure of the LLM Backend Framework.

## Overview

The project is organized into several key directories:

```
├── api/                  # API layer with FastAPI
│   ├── v1/               # Versioned APIs
│   ├── middleware/       # API middleware components
│   ├── app.py            # API application configuration
│   ├── models.py         # API data models
│   └── routes.py         # API route definitions
├── src/                  # Source code
│   ├── bot.py            # Bot implementation
│   ├── reasoning/        # Reasoning components
│   │   ├── brains/       # LLM-powered reasoning
│   │   │   ├── services/ # Brain service implementations
│   │   └── chain_manager.py # Chain manager implementation
│   ├── memory/           # Conversation memory modules
│   ├── llms/             # LLM abstraction layer
│   │   ├── base.py       # Base LLM client interface
│   │   └── clients/      # LLM-specific client implementations
│   ├── common/           # Shared utilities and models
│   │   ├── objects.py    # Shared data models
│   │   └── config.py     # Configuration management
│   └── tools/            # Tools for agent capabilities
├── infrastructure/       # Infrastructure concerns
│   ├── db/               # Database clients
│   └── di/               # Dependency injection
├── tests/                # Test directory
├── docs/                 # Documentation
├── app.py                # FastAPI application
├── cli.py                # Command-line interface
└── requirements.txt      # Project dependencies
```

## Key Files

### API Layer

- `api/v1/chat.py` - Chat endpoints
- `api/v1/health.py` - Health check endpoints
- `api/v1/__init__.py` - API initialization
- `api/app.py` - API application configuration
- `app.py` - FastAPI main application

### Bot Implementation

- `src/bot.py` - Main Bot class

### Reasoning Components

- `src/reasoning/brains/base.py` - `BaseBrain` abstract class
- `src/reasoning/brains/brain_factory.py` - Factory to create brains
- `src/reasoning/brains/services/openai_brain.py` - OpenAI brain implementation
- `src/reasoning/brains/services/llama_brain.py` - LlamaCpp brain implementation
- `src/reasoning/brains/services/azure_openai_brain.py` - Azure OpenAI brain implementation
- `src/reasoning/chain_manager.py` - Chain manager for reasoning flows

### Memory Modules

- `src/memory/base_memory.py` - `BaseChatbotMemory` abstract class
- `src/memory/custom_memory.py` - In-memory implementation
- `src/memory/mongodb_memory.py` - MongoDB implementation

### LLM Clients

- `src/llms/base.py` - `BaseLLMClient` abstract class
- `src/llms/clients/openai_client.py` - OpenAI client
- `src/llms/clients/llamacpp_client.py` - LlamaCpp client
- `src/llms/clients/azure_openai_client.py` - Azure OpenAI client
- `src/llms/clients/vertex_client.py` - Google Vertex AI client

### Tools

- `src/tools/base.py` - `BaseTool` abstract class
- `src/tools/serp.py` - Search tool implementation

### Common Utilities

- `src/common/objects.py` - Shared data models
- `src/common/config.py` - Configuration management

### Infrastructure

- `infrastructure/db/mongodb.py` - MongoDB client
- `infrastructure/di/container.py` - Dependency injection container

### Testing

- `tests/conftest.py` - Pytest fixtures
- `tests/bot/test_bot.py` - Bot tests
- `tests/reasoning/test_chain_manager.py` - Chain manager tests
- `tests/reasoning/brains/test_brain_factory.py` - Brain factory tests
- `tests/memory/test_memory.py` - Memory tests

### Documentation

- `docs/architecture.md` - Architecture guide
- `docs/extending.md` - Extension guide
- `docs/api.md` - API documentation
- `docs/folder_structure.md` - This document
- `docs/improvement_suggestions.md` - Suggestions for future enhancements

### Configuration

- `requirements.txt` - Project dependencies
