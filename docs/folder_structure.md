# Folder Structure

This document describes the folder structure of the LLM Backend Framework.

## Overview

The project is organized into several key directories:

```
├── api/                  # API layer with FastAPI
│   ├── v1/               # Versioned APIs
│   ├── middleware/       # API middleware components
│   ├── app.py            # API application configuration
│   └── __init__.py       # API initialization
├── src/                  # Source code
│   ├── chat_engine.py    # Chat engine implementation
│   ├── config_injector.py # Dependency injection setup
│   ├── base/             # Core framework pieces
│   │   ├── brains/       # Brain interface and variants
│   │   └── components/   # Modular building blocks
│   │       ├── llms/     # LLM client implementations
│   │       ├── memories/ # Conversation memory backends
│   │       ├── embeddings/ # Embedding generators
│   │       ├── tools/    # Tool implementations
│   │       └── vector_databases/ # Vector DB integrations
│   ├── experts/          # Domain-specific chat experts
│   │   ├── qna/          # Q&A expert implementation
│   │   └── rag_bot/      # Retrieval‑augmented generation expert
│   └── common/           # Shared utilities
├── tests/               # Test directory
├── docs/                # Documentation
├── app.py               # FastAPI application entry point
├── cli.py               # Command-line interface
├── Dockerfile           # Docker configuration
├── Makefile            # Build and development commands
├── pyproject.toml      # Python project configuration
└── requirements.txt    # Project dependencies
```

## Key Components

### API Layer (`api/`)

The API layer handles HTTP requests and responses using FastAPI:

- `api/v1/` - Versioned API endpoints
- `api/middleware/` - Custom middleware components
- `api/app.py` - FastAPI application configuration
- `api/__init__.py` - API initialization

### Source Code (`src/`)

#### Chat Engine
- `src/chat_engine.py` - Chat engine implementation for message processing
- `src/config_injector.py` - Dependency injection configuration

#### Base Layer (`src/base/`)
- `src/base/brains/` - Brain interfaces and variants
- `src/base/components/` - Core components
  - `llms/` - LLM client implementations
  - `memories/` - Conversation memory implementations
  - `embeddings/` - Embedding generators
  - `tools/` - Tool implementations
  - `vector_databases/` - Vector database integrations
  - `README.md` - Components documentation

#### Experts (`src/experts/`)
- Domain-specific experts built on top of the base layer
- `qna/` - Question answering expert
- `rag_bot/` - Retrieval‑augmented generation expert

#### Common Utilities (`src/common/`)
- Shared utilities and models
- Configuration management
- Logging setup

### Testing (`tests/`)
- Unit tests
- Integration tests
- Test fixtures and utilities

### Documentation (`docs/`)
- `api.md` - API documentation
- `folder_structure.md` - This document

## Architecture Overview

The application follows a layered architecture:

1. **API Layer**
   - Handles HTTP requests/responses
   - Input validation
   - Error handling
   - Middleware processing

2. **Base Layer**
   - Brain abstractions and component factories
   - Chat engine integration

3. **Experts**
   - Domain-specific logic built on the base layer

4. **Common Layer**
   - Shared utilities
   - Configuration management
   - Logging

This structure promotes:
- Clear separation of concerns
- Modularity and extensibility
- Easy testing and maintenance
- Consistent error handling
- Comprehensive logging
