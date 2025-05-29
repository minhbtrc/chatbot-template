# LLM Chatbot Backend Framework

A modular backend framework for building AI chat applications powered by large language models (LLMs), using FastAPI and MongoDB. This framework incorporates the latest techniques and best practices for building production-ready chatbots.

## Features

- 🧠 **Flexible Brain Architecture**: Support for multiple LLM providers (OpenAI, Azure OpenAI, LlamaCpp, Vertex AI)
- 🔄 **Conversation Management**: Robust conversation history handling with multiple storage backends
- 🛠️ **Extensible Tool System**: Easy integration of custom tools and capabilities
- 📝 **Comprehensive Logging**: Detailed logging throughout the application lifecycle
- 🔒 **Error Handling**: Robust error management with custom exceptions
- 🚀 **FastAPI Integration**: Modern, async API with automatic documentation
- 🔌 **Dependency Injection**: Clean component management and configuration
- 🧪 **Testing Support**: Built-in testing infrastructure
- 📚 **RAG Support**: Built-in support for Retrieval-Augmented Generation with document processing and vector storage
- 🎯 **Streaming Chat**: Real-time streaming responses using Server-Sent Events (SSE)
- 🖥️ **Streaming CLI**: Interactive command-line interface with real-time token streaming
- 🗄️ **SQL Memory System**: Persistent conversation storage with repository pattern and user management
- ⚡ **Async Support**: Full asynchronous operation support for high-performance applications

## Quick Start

### Prerequisites

- Python 3.12+
- MongoDB (for persistent memory)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Installation

1. Clone the repository
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
   
   # MongoDB Configuration
   MONGO_URI=mongodb://localhost:27017/chatbot
   MONGO_DATABASE=langchain_bot
   MONGO_COLLECTION=chatbot
   
   # Vector Database Configuration
   VECTOR_DATABASE_TYPE=CHROMA
   VECTOR_DATABASE_CHROMA_PATH=./chroma_db
   
   # Embedding Configuration
   EMBEDDING_TYPE=AZUREOPENAI
   AZURE_EMBEDDING_MODEL_KEY=your_azure_key
   AZURE_EMBEDDING_MODEL_ENDPOINT=your_endpoint
   AZURE_EMBEDDING_MODEL_DEPLOYMENT=your_deployment
   AZURE_EMBEDDING_MODEL_VERSION=2024-02-15-preview
   
   # Server Configuration
   PORT=8080
   HOST=0.0.0.0
   LOG_LEVEL=INFO
   ```

### Running the Application

1. Start the API server:
   ```bash
   python app.py
   ```
   The API will be available at http://localhost:8080

2. Use the CLI for testing:
   ```bash
   # Basic chat usage
   python cli.py
   
   # Specify a model type
   python cli.py --model llama
   
   # Enable streaming responses (real-time token-by-token output)
   python cli.py --stream
   
   # Combine options for streaming with specific model
   python cli.py --model azureopenai --stream
   
   # Use RAG bot with document processing
   python rag_cli.py --document path/to/your/document.pdf
   ```

### CLI Options

The CLI supports several options for customizing your chat experience:

**Main CLI (`cli.py`)**:
- `--model`: Choose the LLM model type (`openai`, `llama`, `azureopenai`)
- `--stream`: Enable real-time streaming responses (see tokens appear as they're generated)
- `--conversation-id`: Set a custom conversation ID for session persistence

**RAG CLI (`rag_cli.py`)**:
- `--model`: Choose the LLM model type
- `--document`: Process and index a document for RAG queries
- `--conversation-id`: Set a custom conversation ID

Examples:
```bash
# Stream responses with Azure OpenAI
python cli.py --model azureopenai --stream --conversation-id my_session

# Process a PDF and start RAG chat
python rag_cli.py --document report.pdf --model openai
```

## Documentation

📚 **Detailed documentation is available in the [docs/](./docs/) folder:**

- [API Documentation](./docs/api.md) - Complete API reference and examples
- [Streaming Chat API](./docs/streaming_api.md) - Real-time streaming chat implementation and usage
- [SQL Memory System](./docs/sql_memory.md) - SQL-based conversation storage with repository pattern
- [Quick Start: SQL & Streaming](./docs/quick_start_streaming_sql.md) - Fast setup guide for new features
- [Database Documentation](./docs/database.md) - Database models and configuration
- [Conversation Management](./docs/conversation_management_api.md) - Advanced conversation handling
- [Folder Structure](./docs/folder_structure.md) - Project organization and architecture
- [Error Handling](./docs/api.md#error-handling) - Error handling and best practices
- [Logging](./docs/api.md#logging) - Logging configuration and usage

## Project Structure

```
├── api/                  # API layer with FastAPI
├── src/                  # Source code
│   ├── bot.py           # Main Bot class
│   ├── chat_engine.py   # Chat engine implementation
│   ├── experts/         # Expert implementations (RAG, etc.)
│   ├── components/      # Components Layer
│   └── common/          # Shared utilities
├── tests/              # Test directory
└── docs/              # Documentation
```

## Development

### Code Quality

```bash
# Run linting
flake8 .

# Clean up build files
make clean
```

### Docker Support

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository.
