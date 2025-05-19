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
│   ├── core/             # Core application logic
│   │   ├── bot.py        # Main Bot class
│   │   ├── brains/       # Brain implementations
│   │   └── components/   # Reusable components
│   │       ├── llms/     # LLM client implementations
│   │       ├── memory/   # Memory implementations
│   │       ├── tools/    # Tool implementations
│   │       └── README.md # Components documentation
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

#### Core Layer (`src/core/`)
- `src/core/bot.py` - Main Bot class that orchestrates components
- `src/core/brains/` - Brain implementations for different reasoning strategies
- `src/core/components/` - Reusable components
  - `llms/` - LLM client implementations
  - `memory/` - Memory storage implementations
  - `tools/` - Tool implementations
  - `README.md` - Components documentation

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

2. **Core Layer**
   - Bot orchestration
   - Chat engine processing
   - Brain implementations
   - Component coordination

3. **Components Layer**
   - Modular, interchangeable components
   - LLM clients
   - Memory implementations
   - Tool implementations

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
