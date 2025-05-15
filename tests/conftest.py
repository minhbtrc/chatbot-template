"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from api import create_app
from src.common.config import Config
from infrastructure.di.container import container
from src.reasoning.brains.services.openai_brain import OpenAIBrain
from src.reasoning.brains.services.llama_brain import LlamaBrain


@pytest.fixture
def config():
    """Fixture for application configuration."""
    return Config()


@pytest.fixture
def test_client():
    """Fixture for FastAPI test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_openai_brain():
    """Fixture for mocked OpenAI brain."""
    # Override the container's openai brain factory
    with container.openai_brain.override(lambda: OpenAIBrain(
        llm_client=None,
        config=Config(),
        tools=None,
        model_kwargs={"model_name": "gpt-3.5-turbo-test"}
    )):
        # Patch the model to avoid actual API calls
        container.openai_client.reset_override()
        yield container.openai_brain()


@pytest.fixture
def mock_llama_brain():
    """Fixture for mocked LlamaCpp brain."""
    # Override the container's llama brain factory
    with container.llama_brain.override(lambda: LlamaBrain(
        llm_client=None,
        config=Config(),
        tools=None,
        model_kwargs={"model_path": "/path/to/mock/model.bin"}
    )):
        # Patch the model to avoid actual model loading
        container.llama_client.reset_override()
        yield container.llama_brain()


@pytest.fixture
def mock_bot(mock_openai_brain):
    """Fixture for mocked Bot."""
    from src.bot import Bot
    from src.components.memory.custom_memory import InMemory
    
    memory = InMemory()
    return Bot(brain=mock_openai_brain, memory=memory)


@pytest.fixture
def mock_mongodb(monkeypatch):
    """Fixture for mocked MongoDB client."""
    # Create a mock for MongoDB operations
    class MockMongoClient:
        def __init__(self, *args, **kwargs):
            self.data = {}
        
        def __getitem__(self, name):
            return self
        
        def find_one(self, query):
            for key, value in query.items():
                if key in self.data and self.data[key] == value:
                    return self.data
            return None
        
        def insert_one(self, document):
            class Result:
                @property
                def inserted_id(self):
                    return "mock_id"
            
            self.data.update(document)
            return Result()
        
        def close(self):
            pass
    
    # Patch the MongoDB client
    monkeypatch.setattr("pymongo.MongoClient", MockMongoClient)
    
    return MockMongoClient() 