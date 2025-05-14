# Folder Structure

This document explains the folder structure of the application.

## Current Structure

The application is organized as follows:

```
├── api/                  # API layer with FastAPI
│   └── v1/               # Versioned APIs
├── src/                  # Source code
│   ├── bot/              # Bot implementation
│   ├── reasoning/        # Reasoning components
│   │   ├── brains/       # LLM-powered reasoning
│   │   └── chains/       # Chain implementations
│   ├── memory/           # Conversation memory modules
│   ├── llm_clients/      # LLM service wrappers
│   ├── common/           # Shared models
│   │   └── models.py     # Data models
│   ├── tools/            # Tools for agent capabilities
│   └── prompts/          # Prompt templates
├── infrastructure/       # Infrastructure concerns
│   ├── db/               # Database clients
│   ├── di/               # Dependency injection
│   ├── base.py           # Base classes
│   ├── config.py         # App configuration
│   ├── constants.py      # App-wide constants
│   └── logging.py        # Logging utilities
├── tests/                # Test directory
├── docs/                 # Documentation
├── cli.py                # Command-line interface
└── app.py                # FastAPI application
```

## Module Responsibilities

### API Layer

The API layer handles HTTP requests and responses using FastAPI. It provides endpoints for chat, health checks, and other functionality.

### Source Code

The `src` directory contains the core application logic:

- **bot**: The Bot class that coordinates between reasoning, tools, and memory
- **reasoning**: Components for generating responses using LLMs
- **memory**: Storage implementations for conversation history
- **llm_clients**: Wrappers for different LLM providers
- **common**: Shared models used throughout the application
- **tools**: Implementations of tools for enhanced capabilities
- **prompts**: Templates for prompts used with LLMs

### Infrastructure

The `infrastructure` directory handles application-wide concerns:

- **db**: Database clients for storage
- **di**: Dependency injection
- **base.py**: Base classes used throughout the application
- **config.py**: Configuration management
- **constants.py**: Application-wide constants
- **logging.py**: Centralized logging

### CLI

The `cli.py` file provides a command-line interface for testing the chatbot without running the API server.

### Tests

The `tests` directory contains unit and integration tests for the application.

### Documentation

The `docs` directory contains detailed documentation for the application.
