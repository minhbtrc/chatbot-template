# Extending the Framework

This document provides guidelines for extending the LLM Backend Framework with new components.

## Adding a New LLM Client

To add support for a new LLM provider:

1. **Create a new client file** in `src/llm_clients/`:

```python
# src/llm_clients/custom_client.py
from typing import Dict, Any, List, Union
from src.llms.base import BaseLLMClient

class CustomLLMClient(BaseLLMClient):
    def __init__(self, config):
        self.config = config
        # Initialize your client here
        self.client = YourProviderSDK(api_key=config.custom_api_key)
        
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        # Implement chat functionality
        # Convert messages to format expected by provider
        response = self.client.generate_chat(messages, **kwargs)
        return response.text
        
    def complete(self, prompt: str, **kwargs: Any) -> str:
        # Implement completion functionality
        response = self.client.generate_text(prompt, **kwargs)
        return response.text
        
    def create_embedding(self, text: Union[str, List[str]], **kwargs: Any) -> List[List[float]]:
        # Implement embedding functionality
        if isinstance(text, str):
            text = [text]
        embeddings = self.client.get_embeddings(text, **kwargs)
        return embeddings
        
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "CustomProvider",
            "model": self.client.model_name,
            # Add other relevant info
        }
```

2. **Update the client factory** (if applicable):
```python
# If you have a client factory
def create_llm_client(config, provider="openai"):
    if provider == "custom":
        return CustomLLMClient(config)
    # ...
```

3. **Add unit tests** in `tests/llm_clients/`:
```python
# tests/llm_clients/test_custom_client.py
def test_custom_client_chat():
    # Test chat functionality
    # ...
```

## Adding a New Brain

To add a new brain implementation:

1. **Create a new brain file** in `src/reasoning/brains/`:

```python
# src/reasoning/brains/custom_brain.py
from typing import Dict, Any, Optional, List
from src.reasoning.brains.base import BaseBrain

class CustomBrain(BaseBrain):
    def __init__(self, config, llm_client, model_kwargs=None):
        self.config = config
        self.llm_client = llm_client
        self.model_kwargs = model_kwargs or {}
        self.tools = []
        
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Implement your custom reasoning logic here
        # This could involve:
        # - Specialized prompting
        # - Multi-step reasoning
        # - Tool usage patterns
        
        # Example of using the LLM client:
        messages = self._format_messages(query, context)
        response = self.llm_client.chat(messages, **self.model_kwargs)
        return response
        
    def _format_messages(self, query, context):
        # Helper method to format messages
        # ...
        
    def reset(self) -> None:
        # Reset any stateful components
        pass
        
    def use_tools(self, tools: List[Any]) -> None:
        self.tools = tools
        # Configure how tools are used in your brain
```

2. **Update the brain factory** in `src/reasoning/brains/brain_factory.py`:

```python
def create_custom_brain(config, model_kwargs=None, **kwargs) -> BaseBrain:
    """Create a custom brain implementation."""
    # Import and create the appropriate LLM client
    from src.llm_clients.custom_client import CustomLLMClient
    llm_client = CustomLLMClient(config)
    
    # Create default parameters if not provided
    if not model_kwargs:
        model_kwargs = {
            "parameter1": getattr(config, "custom_param1", "default"),
            "parameter2": getattr(config, "custom_param2", 0.5),
        }
    
    # Create and return the brain
    return CustomBrain(
        config=config,
        llm_client=llm_client,
        model_kwargs=model_kwargs,
        **kwargs
    )

def create_brain(config, brain_type=None, **kwargs):
    # Update to include your new brain type
    brain_type = brain_type or getattr(config, "model_type", "openai").lower()
    
    if brain_type == "custom":
        return create_custom_brain(config, **kwargs)
    # ... existing brain types
```

3. **Update the brain imports** in `src/reasoning/brains/__init__.py`:

```python
from src.reasoning.brains.custom_brain import CustomBrain
from src.reasoning.brains.brain_factory import create_custom_brain

__all__ = [
    # ... existing brains
    "CustomBrain",
    "create_custom_brain",
]
```

4. **Add unit tests** in `tests/reasoning/brains/`:

```python
# tests/reasoning/brains/test_custom_brain.py
def test_custom_brain_think():
    # Test the custom brain's thinking
    # ...
```

## Adding a New Tool

To add a new tool:

1. **Create a new tool file** in `src/tools/`:

```python
# src/tools/custom_tool.py
from typing import Dict, Any
from src.tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self, api_key=None):
        super().__init__(
            name="custom_tool",
            description="A tool that performs custom functionality"
        )
        self.api_key = api_key
        # Initialize any resources needed
        
    def run(self, input_data: str) -> str:
        """Execute the tool with the given input."""
        # Implement your tool's functionality
        result = self._process_input(input_data)
        return result
        
    def _process_input(self, input_data):
        # Helper method to process the input
        # ...
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the tool's parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The input for the custom tool"
                }
            },
            "required": ["query"]
        }
```

2. **Register the tool** (if you have a tool registry):

```python
# src/tools/registry.py
from src.tools.custom_tool import CustomTool

def get_available_tools(config):
    tools = []
    
    # Add your tool if configured
    if hasattr(config, "use_custom_tool") and config.use_custom_tool:
        tools.append(CustomTool(api_key=config.custom_tool_api_key))
    
    # ... other tools
    return tools
```

3. **Add unit tests** in `tests/tools/`:

```python
# tests/tools/test_custom_tool.py
def test_custom_tool_run():
    # Test the custom tool's functionality
    # ...
```

## Adding a New Memory Implementation

To add a new memory system:

1. **Create a new memory file** in `src/memory/`:

```python
# src/memory/custom_memory.py
from typing import List, Dict, Any
from src.memory.base_memory import BaseChatbotMemory

class CustomMemory(BaseChatbotMemory):
    def __init__(self, config):
        self.config = config
        # Initialize your memory system
        
    def add_message(self, role: str, content: str, conversation_id: str) -> None:
        # Store a message in your memory system
        # ...
        
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        # Retrieve conversation history
        # ...
        
    def clear_history(self, conversation_id: str) -> None:
        # Clear the history for a conversation
        # ...
```

2. **Add unit tests** in `tests/memory/`:

```python
# tests/memory/test_custom_memory.py
def test_custom_memory_add_and_retrieve():
    # Test adding and retrieving messages
    # ...
```

## Best Practices

### Type Annotations

Always use type annotations for better code safety:

```python
def method_name(param1: Type1, param2: Type2) -> ReturnType:
    # Implementation
```

### Documentation

Include detailed docstrings for all classes and methods:

```python
class MyClass:
    """
    Class description explaining its purpose and usage.
    """
    
    def my_method(self, param1: str) -> bool:
        """
        Method description.
        
        Args:
            param1: Description of parameter
            
        Returns:
            Description of return value
        """
```

### Error Handling

Implement proper error handling for external services:

```python
try:
    result = external_service.call()
except ExternalServiceError as e:
    logger.error(f"External service error: {e}")
    # Handle gracefully
```

### Testing

Create thorough unit tests for new components:

- Test happy paths
- Test edge cases
- Mock external dependencies
- Test error handling 