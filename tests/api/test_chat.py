"""
Tests for the chat API endpoints.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from api.v1.models import ChatRequest
from core.bot import Bot


def test_chat_endpoint(test_client):
    """Test the chat endpoint."""
    # Create a mock bot with a call method that returns a test response
    mock_bot = MagicMock(spec=Bot)
    mock_bot.call.return_value = {
        "response": "This is a test response",
        "conversation_id": "test_conversation"
    }
    
    # Set the bot on the app state
    test_client.app.state.bot = mock_bot
    
    # Create a test request
    request_data = {
        "input": "Hello, test bot!",
        "conversation_id": "test_conversation"
    }
    
    # Send a POST request to the chat endpoint
    response = test_client.post("/api/v1/chat", json=request_data)
    
    # Check that the response is valid
    assert response.status_code == 200
    data = response.json()
    assert "output" in data
    assert data["output"] == "This is a test response"
    assert data["conversation_id"] == "test_conversation"
    
    # Verify the bot was called with the right parameters
    mock_bot.call.assert_called_once_with(
        sentence="Hello, test bot!",
        conversation_id="test_conversation"
    )


def test_clear_history_endpoint(test_client):
    """Test the clear history endpoint."""
    # Create a mock bot with a reset_history method
    mock_bot = MagicMock(spec=Bot)
    mock_bot.reset_history.return_value = None
    
    # Set the bot on the app state
    test_client.app.state.bot = mock_bot
    
    # Send a POST request to the clear history endpoint
    response = test_client.post("/api/v1/clear/test_conversation")
    
    # Check that the response is valid
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "History for conversation test_conversation cleared" in data["message"]
    
    # Verify the bot was called with the right parameters
    mock_bot.reset_history.assert_called_once_with(
        conversation_id="test_conversation"
    ) 