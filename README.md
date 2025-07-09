# LLM Chatbot Backend Framework

A modular, production-ready backend framework for building AI chat applications powered by large language models (LLMs), using FastAPI and dependency injection. This framework supports multiple expert types and incorporates the latest techniques for building scalable chatbot applications.

## Features

### 🤖 AI & LLM Integration
- 🧠 **Multiple Expert Types**: Support for different chat modes:
  - **QNA**: Basic question-answering chatbot
  - **RAG**: Retrieval-Augmented Generation with document processing
  - **DEEPRESEARCH**: Advanced research assistant with web search capabilities
- 🔄 **Flexible LLM Support**: Multiple LLM providers (OpenAI, Azure OpenAI, LlamaCpp, Vertex AI)
- 🎯 **Streaming Responses**: Real-time streaming chat using Server-Sent Events (SSE)
- 📚 **Document Processing**: Built-in PDF processing and vector storage for RAG

### 💬 Conversation & Memory Management
- 🗄️ **Multiple Memory Backends**: In-memory, MongoDB, and SQL storage options
- 🔄 **Conversation History**: Persistent conversation management with user sessions
- 🧹 **Memory Operations**: Clear, retrieve, and manage conversation history

### 🛠️ Development & Architecture
- 🚀 **FastAPI Integration**: Modern, async API with automatic OpenAPI documentation
- 🔌 **Dependency Injection**: Clean component management using the Injector pattern
- ⚡ **Async Support**: Full asynchronous operation for high-performance applications
- 🧪 **Extensible Tool System**: Easy integration of custom tools (web search, etc.)

### 🔧 Operations & Reliability
- 📝 **Comprehensive Logging**: Detailed logging with configurable levels
- 🔒 **Error Handling**: Robust error management with custom middleware
- 🧪 **Testing Infrastructure**: Complete test suite with async support
- 🐳 **Docker Support**: Containerized deployment ready

### 🖥️ User Interfaces
- 🖥️ **Multiple CLI Modes**: Interactive command-line interfaces for different bot types
- 🎨 **Colorized Output**: Beautiful terminal interface with colored responses
- 📊 **Streaming CLI**: Real-time token-by-token response streaming

## Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (optional, for persistent memory)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Install dependencies using uv:
   ```bash
   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows

   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Core Configuration
   MODEL_TYPE=OPENAI  # Options: OPENAI, LLAMA, AZUREOPENAI, VERTEX
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_key
   BASE_MODEL_NAME=gpt-3.5-turbo
   
   # Azure OpenAI Configuration (if using Azure)
   AZURE_CHAT_MODEL_KEY=your_azure_key
   AZURE_CHAT_MODEL_VERSION=2024-02-15-preview
   AZURE_CHAT_MODEL_ENDPOINT=your_endpoint
   AZURE_CHAT_MODEL_DEPLOYMENT=your_deployment
   
   # MongoDB Configuration (optional)
   MONGO_URI=mongodb://localhost:27017/chatbot
   MONGO_DATABASE=langchain_bot
   MONGO_COLLECTION=chatbot
   
   # Vector Database Configuration
   VECTOR_DATABASE_TYPE=CHROMA
   VECTOR_DATABASE_CHROMA_PATH=./chroma_db
   
   # Embedding Configuration (for RAG)
   EMBEDDING_TYPE=AZUREOPENAI
   AZURE_EMBEDDING_MODEL_KEY=your_azure_key
   AZURE_EMBEDDING_MODEL_ENDPOINT=your_endpoint
   AZURE_EMBEDDING_MODEL_DEPLOYMENT=your_deployment
   AZURE_EMBEDDING_MODEL_VERSION=2024-02-15-preview
   
   # Tavily Search (for DEEPRESEARCH)
   TAVILY_API_KEY=your_tavily_key
   
   # Server Configuration
   PORT=8080
   HOST=0.0.0.0
   LOG_LEVEL=INFO
   ```

### Running the Application

#### 1. API Server
Start the FastAPI server:
```bash
python app.py
```
The API will be available at http://localhost:8080 with automatic documentation at http://localhost:8080/docs

#### 2. Command Line Interface

The framework provides a unified CLI with three specialized bot modes:

**QNA Bot** - Basic question-answering:
```bash
# Basic usage
python cli.py --mode qna

# With custom model and streaming
python cli.py --mode qna --model azureopenai --stream
```

**RAG Bot** - Document-aware chat:
```bash
# Basic RAG chat
python cli.py --mode rag

# Process a document and chat about it
python cli.py --mode rag --document path/to/document.pdf --stream

# With custom model
python cli.py --mode rag --model openai --conversation-id doc_session
```

**DeepResearch Bot** - Advanced research assistant:
```bash
# Research mode with web search capabilities
python cli.py --mode deepresearch

# With streaming and custom model
python cli.py --mode deepresearch --model azureopenai --stream
```

### CLI Features & Commands

All CLI modes support:
- `exit` or `quit`: Exit the chat
- `clear`: Clear conversation history
- `Ctrl+C`: Force exit
- `--stream`: Enable real-time token streaming
- `--model`: Choose LLM provider (openai, llama, azureopenai)
- `--conversation-id`: Set custom session ID

**RAG-specific features:**
- `--document`: Process and index documents (PDF, TXT, etc.)
- Document question-answering based on uploaded content

**DeepResearch-specific features:**
- Web search integration for current information
- Advanced reasoning and research capabilities

## API Endpoints

The REST API provides the following endpoints:

### Chat Endpoints
- `POST /api/v1/chat/message` - Send a message and get response
- `POST /api/v1/chat/stream` - Stream chat responses (SSE)
- `DELETE /api/v1/chat/clear` - Clear conversation history

### Expert Management
- `GET /api/v1/experts/available` - List available expert types
- `POST /api/v1/experts/switch` - Switch between expert types

### RAG Operations
- `POST /api/v1/rag/upload` - Upload and process documents
- `GET /api/v1/rag/documents` - List processed documents
- `DELETE /api/v1/rag/documents/{doc_id}` - Delete a document

### Health & Status
- `GET /api/v1/health` - Health check endpoint
- `GET /` - API documentation redirect

## Project Structure

```
backend/
├── api/                          # FastAPI application layer
│   ├── app.py                   # FastAPI app factory and configuration
│   ├── middleware/              # Custom middleware (error handling)
│   └── v1/                      # API v1 endpoints
│       ├── chat.py             # Chat endpoints
│       ├── experts.py          # Expert management
│       ├── rag.py              # RAG operations
│       ├── health.py           # Health checks
│       └── models.py           # API request/response models
├── src/                         # Core application logic
│   ├── base/                   # Base components and factories
│   │   ├── brains/             # LLM brain implementations
│   │   ├── components/         # Core components (LLMs, embeddings, etc.)
│   │   └── memories/           # Memory backend implementations
│   ├── experts/                # Expert implementations
│   │   ├── qna/               # Basic Q&A expert
│   │   ├── rag_bot/           # RAG-powered expert
│   │   └── deepresearch_bot/  # Research expert with web search
│   ├── common/                # Shared utilities
│   │   ├── config.py          # Configuration management
│   │   ├── logging.py         # Logging setup
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── schemas.py         # Data models
│   ├── chat_engine.py         # Main chat engine
│   └── config_injector.py     # Dependency injection setup
├── clis/                       # Command line interfaces
│   ├── cli.py                 # QNA bot CLI
│   ├── rag_cli.py             # RAG bot CLI
│   └── deepresearch_cli.py    # DeepResearch bot CLI
├── tests/                      # Test suite
├── docs/                       # Documentation
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Docker configuration
└── Makefile                   # Build and deployment scripts
```

## Architecture

The framework follows Clean Architecture principles with clear separation of concerns:

### Core Components
- **Chat Engine**: Orchestrates conversations between users and experts
- **Experts**: Specialized AI assistants (QNA, RAG, DeepResearch)
- **Brains**: LLM abstraction layer supporting multiple providers
- **Memory**: Conversation storage with pluggable backends
- **Tools**: External capabilities (web search, document processing)

### Dependency Injection
The framework uses the Injector pattern for clean dependency management:
- Configuration-driven component initialization
- Easy testing with mock dependencies
- Modular and extensible architecture

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run integration tests
pytest -m integration
```

### Code Quality
```bash
# Run linting
flake8 .

# Type checking
mypy src/

# Clean up build files
make clean
```

### Docker Support
```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Docker Compose (if available)
docker-compose up
```

## Configuration

The application uses environment variables for configuration. Key settings:

### Required Settings
- `MODEL_TYPE`: LLM provider (OPENAI, AZUREOPENAI, LLAMA, VERTEX)
- `OPENAI_API_KEY` or equivalent provider keys

### Optional Settings
- `MONGO_URI`: MongoDB connection for persistent memory
- `VECTOR_DATABASE_TYPE`: Vector database type (CHROMA, INMEMORY)
- `TAVILY_API_KEY`: Web search API key for DeepResearch
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines
- Follow Clean Architecture principles
- Write comprehensive tests
- Use type hints throughout
- Follow existing code style and patterns
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

📚 **Detailed documentation is available in the [docs/](./docs/) folder:**

- [API Documentation](./docs/api.md) - Complete API reference and examples
- [Folder Structure](./docs/folder_structure.md) - Project organization and architecture
- [Expert Switching](./docs/EXPERT_SWITCHING_README.md) - Guide to switching between bot types
