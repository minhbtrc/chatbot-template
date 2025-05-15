"""
Tests for the chat API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.models import ChatRequest


def test_chat_endpoint(test_client, monkeypatch):
    """Test the chat endpoint."""
    # Mock the bot call method to return a simple response
    def mock_call(**kwargs):
        return {
            "response": "This is a test response",
            "conversation_id": kwargs.get("conversation_id", "test_conversation")
        }
    
    monkeypatch.setattr("api.v1.chat.bot.call", mock_call)
    
    # Create a test request
    request_data = {
        "input": "Hello, test bot!",
        "conversation_id": "test_conversation"
    }
    
    # Send a POST request to the chat endpoint
    response = test_client.post("/v1/chat", json=request_data)
    
    # Check that the response is valid
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "This is a test response"
    assert data["conversation_id"] == "test_conversation"


def test_clear_history_endpoint(test_client, monkeypatch):
    """Test the clear history endpoint."""
    # Mock the bot reset_history method
    def mock_reset_history(**kwargs):
        return None
    
    monkeypatch.setattr("api.v1.chat.bot.reset_history", mock_reset_history)
    
    # Send a POST request to the clear history endpoint
    response = test_client.post("/v1/clear/test_conversation")
    
    # Check that the response is valid
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "History for conversation test_conversation cleared" in data["message"] 