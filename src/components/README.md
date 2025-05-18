# Components

This folder contains all the core components needed for the chatbot. Components are self-contained objects that provide basic capabilities and have minimal dependencies on other parts of the system.

Key components include:
- LLM clients for interfacing with language models
- Memory implementations for conversation history
- Tools that extend the bot's capabilities

Each component follows a consistent structure and design patterns:

1. Base abstract class defining the interface
2. Concrete implementations of the interface
3. Factory class to instantiate the appropriate implementation

This pattern provides:
- Clear separation of concerns
- Easy extensibility for new implementations
- Runtime configuration through factory pattern
- Dependency injection support

Component Structure:

/component-type/
    /clients/
        client_implementation_1.py
        client_implementation_2.py
    base.py
    factory.py
    __init__.py