# Tests Organization

This directory contains all test files organized by category.

## Structure

```
tests/
├── __init__.py                     # Tests package marker
├── README.md                       # This file
├── conftest.py                     # Pytest configuration and fixtures
├── test_cli.py                     # CLI functionality tests
├── test_database.py                # Database layer tests
├── api/                            # API endpoint tests
│   ├── __init__.py
│   ├── test_chat.py               # Chat API tests
│   ├── test_conversation_apis.py  # Conversation management API tests
│   ├── test_rag_api.py            # RAG API tests
│   └── test_user_chat_integration.py # User integration tests
├── components/                     # Component-level tests
│   ├── __init__.py
│   ├── test_embeddings.py         # Embedding component tests
│   ├── test_llm_client.py         # LLM client tests
│   ├── test_memories.py           # Memory component tests
│   ├── test_sql_memory.py         # SQL memory implementation tests
│   └── test_vectordatabases.py    # Vector database tests
└── tools/                          # Tool-related tests
    ├── __init__.py
    ├── test_base_tool.py          # Base tool tests
    └── test_serp_tool.py          # SERP tool tests
```

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

### Run specific test categories
```bash
# API tests only
python -m pytest tests/api/

# Component tests only
python -m pytest tests/components/

# Tool tests only
python -m pytest tests/tools/
```

### Run specific test files
```bash
# Database tests
python -m pytest tests/test_database.py

# RAG API tests
python -m pytest tests/api/test_rag_api.py

# SQL memory tests
python -m pytest tests/components/test_sql_memory.py
```

### Run with coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Test Categories

### API Tests (`tests/api/`)
- **test_chat.py**: Basic chat endpoint functionality
- **test_conversation_apis.py**: Conversation management endpoints
- **test_rag_api.py**: RAG document processing and query endpoints
- **test_user_chat_integration.py**: End-to-end user authentication and chat integration

### Component Tests (`tests/components/`)
- **test_embeddings.py**: Embedding interface and implementations
- **test_llm_client.py**: LLM client interface and implementations
- **test_memories.py**: Memory interface and implementations
- **test_sql_memory.py**: SQL-based memory implementation
- **test_vectordatabases.py**: Vector database interface and implementations

### Tool Tests (`tests/tools/`)
- **test_base_tool.py**: Base tool interface
- **test_serp_tool.py**: Search engine results tool

### Core Tests (`tests/`)
- **test_cli.py**: Command-line interface functionality
- **test_database.py**: Database layer and repository tests

## Notes

- All test files have been moved from the root directory to maintain organization
- Import paths have been updated where necessary
- Each test package has its own `__init__.py` file for proper Python package structure
- Tests can be run individually or as a complete suite
- The `conftest.py` file contains shared fixtures and pytest configuration 