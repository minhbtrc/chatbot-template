"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from api import create_app
from src.common.config import Config
from src.core.brains import LLMBrain


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
def mock_brain(monkeypatch):
    """Fixture for mocked Brain."""
    # Create a mock brain
    return LLMBrain(
        llm_client=None,
        config=Config(),
    )


@pytest.fixture
def mock_bot(mock_brain):
    """Fixture for mocked Bot."""
    from src.core.bot import Bot
    from src.core.components.memory import InMemory
    from src.core.components.tools import ToolProvider
    
    memory = InMemory()
    tool_provider = ToolProvider()
    return Bot(brain=mock_brain, memory=memory, tool_provider=tool_provider)


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