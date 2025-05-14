"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from api import create_app
from infrastructure.config import Config
from infrastructure.di.container import container
from src.bots.openai_bot import OpenAIBot
from src.bots.llama_bot import LlamaBot


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
def mock_openai_bot():
    """Fixture for mocked OpenAI bot."""
    # Override the container's openai bot factory
    with container.openai_bot.override(lambda: OpenAIBot(
        config=Config(),
        chain_manager=None,
        memory=None,
        tools=None,
        model_kwargs={"model_name": "gpt-3.5-turbo-test"}
    )):
        # Patch the model to avoid actual API calls
        container.openai_client.reset_override()
        yield container.openai_bot()


@pytest.fixture
def mock_llama_bot():
    """Fixture for mocked LlamaCpp bot."""
    # Override the container's llama bot factory
    with container.llama_bot.override(lambda: LlamaBot(
        config=Config(),
        chain_manager=None,
        memory=None,
        tools=None,
        model_kwargs={"model_path": "/path/to/mock/model.bin"}
    )):
        # Patch the model to avoid actual model loading
        container.llama_client.reset_override()
        yield container.llama_bot()


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