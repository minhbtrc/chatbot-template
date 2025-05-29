"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient

from api import create_app
from src.common.config import Config
from src.base.brains import LLMBrain
from src.database import initialize_database


@pytest.fixture
def config():
    """Fixture for application configuration."""
    return Config()


@pytest.fixture
def test_client():
    """Fixture for FastAPI test client with database initialization."""
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize database for testing
        database_url = f"sqlite:///{temp_db_path}"
        initialize_database(database_url)
        
        # Create the app
        app = create_app()
        
        # Return test client
        yield TestClient(app)
    finally:
        # Clean up temporary database
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


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
    from src.experts.qna.expert import QnaExpert
    from src.base.components.memories import InMemory
    from src.base.components import ToolProvider
    
    memory = InMemory()
    tool_provider = ToolProvider()
    return QnaExpert(brain=mock_brain, memory=memory, tool_provider=tool_provider, config=Config())


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