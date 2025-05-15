# LLM Backend Framework

A modular backend framework for building AI applications with large language models (LLMs), FastAPI, and MongoDB.

📚 **Developer docs available in the [docs/](./docs/) folder.**

📋 **Check out our [improvement suggestions](./docs/improvement_suggestions.md) for future development.**

## Project Structure

The project is organized using the Bot-Brain architecture with standardized interfaces:

```
├── api/                  # API layer with FastAPI
│   ├── v1/               # Versioned APIs
│   │   ├── chat.py       # Chat endpoints
│   │   ├── health.py     # Health check endpoints
│   │   └── __init__.py   # API initialization
│   ├── middleware/       # API middleware components 
│   ├── app.py            # API application configuration
│   ├── models.py         # API data models
│   └── routes.py         # API route definitions
├── src/                  # Source code
│   ├── bot.py            # Main Bot class
│   ├── reasoning/        # Reasoning components
│   │   ├── brains/       # LLM-powered reasoning
│   │   │   ├── base.py   # BaseBrain abstract class
│   │   │   ├── brain_factory.py # Factory to choose correct brain
│   │   │   ├── services/ # Brain service implementations
│   │   │   │   ├── openai_brain.py # Brain using OpenAI LLM
│   │   │   │   ├── llama_brain.py # Brain using LlamaCpp
│   │   │   │   ├── azure_openai_brain.py # Brain using Azure OpenAI
│   │   │   └── __init__.py # Brain module initialization
│   │   └── chain_manager.py # Chain manager for reasoning flows
│   ├── memory/           # Conversation memory modules
│   │   ├── __init__.py   # Memory module initialization
│   │   ├── base_memory.py # BaseChatbotMemory abstract class
│   │   ├── custom_memory.py # In-memory implementation
│   │   └── mongodb_memory.py # MongoDB implementation
│   ├── llms/             # LLM abstraction layer
│   │   ├── base.py       # BaseLLMClient abstract class
│   │   └── clients/      # LLM-specific client implementations
│   │       ├── openai_client.py  # OpenAI API client
│   │       ├── azure_openai_client.py # Azure OpenAI API client
│   │       ├── llamacpp_client.py # LlamaCpp client
│   │       └── vertex_client.py # Google Vertex AI client
│   ├── common/           # Shared utilities and models
│   │   ├── objects.py    # Shared data models
│   │   └── config.py     # Configuration management
│   └── tools/            # Tools for agent capabilities
│       ├── base.py       # BaseTool abstract class
│       ├── serp.py       # Search tool implementation
│       └── __init__.py   # Tools initialization
├── infrastructure/       # Infrastructure concerns
│   ├── db/               # Database clients
│   │   └── mongodb.py    # MongoDB client
│   └── di/               # Dependency injection
├── tests/                # Test directory
│   ├── api/              # API tests
│   ├── bot/              # Bot tests
│   ├── reasoning/        # Reasoning tests
│   │   └── brains/       # Brain tests
│   ├── memory/           # Memory tests 
│   ├── tools/            # Tool tests
│   └── llms/             # LLM client tests
├── docs/                 # Documentation
│   ├── architecture.md   # Architecture guide
│   ├── extending.md      # Extension guide
│   ├── api.md            # API documentation
│   ├── folder_structure.md # Folder structure guide
│   └── improvement_suggestions.md # Suggestions for future improvements
├── app.py                # FastAPI application
├── cli.py                # Command-line interface for local testing
├── Dockerfile            # Docker configuration
└── requirements.txt      # Project dependencies
```

## Architecture

The application follows a Bot-Brain architecture with standardized interfaces:

1. **Bot Layer** - Handles request processing and message coordination
   - A single `Bot` class delegates reasoning to a pluggable `Brain`
   - Manages memory and conversation state

2. **Reasoning Layer** - Responsible for LLM-based reasoning
   - **Brains**: Each brain implementation encapsulates reasoning logic
     - Created by a factory based on configuration
     - Follows a common interface defined by `BaseBrain`
   - **Chains**: Structured reasoning flows for specific tasks

3. **LLM Clients** - Standardized interface for LLM providers
   - Follows `BaseLLMClient` interface
   - Supports chat and completion operations
   - Multiple implementations for different providers (OpenAI, Azure OpenAI, etc.)

4. **Tools** - Standardized interface for agent tools
   - Follows `BaseTool` interface
   - Consistent schema handling with OpenAI tool format
   - Supports a variety of capabilities (search, etc.)

## Bot-Brain Architecture Diagram

```mermaid
graph TD
    %% Entry
    UserInput["User Input"] --> Bot

    %% Bot Layer
    Bot --> BrainFactory
    BrainFactory --> BrainInstance["Brain (via config)"]
    Bot --> Memory
    
    %% Reasoning Layer
    BrainInstance -->|calls| LLMClient
    BrainInstance -->|may use| Tools
    BrainInstance -->|reads/writes| Memory
    
    %% LLM Layer
    LLMClient -->|calls| ExternalAPI["External LLM API"]
    
    %% Tool Layer
    Tools --> SearchTool["Search Tool"]
    Tools --> OtherTools["Other Tools"]
    
    %% Memory Layer
    Memory -->|implementations| StorageOptions["MongoDB / In-Memory"]
    
    %% Configuration
    Config["Configuration"] --> BrainFactory
    Config --> LLMClient
```

### Brain Composition Detail

```mermaid
graph TD
    subgraph Brain
        BrainNode["Brain"] --> ChainManager
        BrainNode --> BrainTools["Brain Tools"]
        BrainNode --> BrainMemory["Brain Memory"]
        ChainManager --> LLMClientNode["LLM Client"]
        ChainManager --> ToolCalls["Tool Calls"]
    end
```

## Implementation Notes

The codebase implements the Bot-Brain architecture with standardized interfaces:

### LLM Client Interface

All LLM clients implement a standard interface:

```python
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
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the LLM model."""
        pass
```

### Tool Interface

Tools follow a standard interface for extension:

```python
class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """Execute the tool with the given input."""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the tool's parameters."""
        pass
    
    def to_openai_tool(self) -> Dict[str, Any]:
        """Convert the tool to an OpenAI tool format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            }
        }
```

### Brain Implementations

Brain implementations are now under the reasoning/brains/services module:

```python
class BaseBrain(ABC):
    @abstractmethod
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process the query and return a response."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the brain's state."""
        pass
```

Different implementations include:
- `OpenAIBrain` - Brain using OpenAI models for reasoning
- `LlamaBrain` - Brain using LlamaCpp for local reasoning
- `AzureOpenAIBrain` - Brain using Azure OpenAI models for reasoning

### Testing

The `tests` directory includes comprehensive tests:

- Mock implementations of `BaseLLMClient` and `BaseTool` for testing
- Unit tests for tools, LLM clients, and other components
- API tests for the FastAPI endpoints

## Status and Extensions

The codebase has been refactored to use standardized interfaces:

1. **✅ Standardized LLM Client Interface**:
   - All LLM clients implement `BaseLLMClient`
   - Consistent methods for chat, completion

2. **✅ Standardized Tool Interface**:
   - All tools implement `BaseTool`
   - Consistent schema definition and execution

3. **✅ Improved Directory Structure**:
   - Renamed directories for clarity (llms → llm_clients, chains → reasoning)
   - Better organization with brains under reasoning/brains/services
   - Consolidated test structure

4. **✅ Enhanced Extensibility**:
   - New LLM clients can be added by implementing `BaseLLMClient`
   - New tools can be added by implementing `BaseTool`
   - Brain implementations can be swapped without changing the Bot

5. **✅ Multiple LLM Providers Support**:
   - OpenAI API integration
   - Azure OpenAI API integration
   - Local LLM support via LlamaCpp
   - Google Vertex AI integration

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB (for persistent memory)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   # For OpenAI
   OPENAI_API_KEY=your_openai_key
   MODEL_TYPE=OPENAI
   
   # For Azure OpenAI
   AZURE_API_KEY=your_azure_openai_key
   AZURE_ENDPOINT=your_azure_endpoint
   AZURE_DEPLOYMENT_NAME=your_deployment_name
   MODEL_TYPE=AZUREOPENAI
   
   # Database
   MONGO_URI=your_mongodb_uri
   ```

### Running the Application

```
python app.py
```

The API will be available at http://localhost:8080

### Using the CLI Interface

For quick testing without running the API server, you can use the command-line interface:

```bash
# Basic usage
python cli.py

# Specify a model type
python cli.py --model llama

# Use Azure OpenAI
python cli.py --model azureopenai

# Specify a custom conversation ID
python cli.py --conversation-id my_session_123
```

Exit the CLI by typing 'exit', 'quit', or pressing Ctrl+C.

## Extending the Framework

### Adding a New LLM Client

1. Create a new file in `src/llms/clients/`
2. Implement the `BaseLLMClient` interface
3. Register the client in the factory if needed

### Adding a New Tool

1. Create a new file in `src/tools/`
2. Implement the `BaseTool` interface
3. Add the tool to the tool registry

### Adding a New Brain

1. Create a new file in `src/reasoning/brains/services/`
2. Implement the `BaseBrain` interface
3. Update the brain factory if needed