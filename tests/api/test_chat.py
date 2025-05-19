"""
Tests for the chat API endpoints.
"""

from unittest.mock import MagicMock

from src.common.schemas import ChatResponse
from src.chat_engine import ChatEngine


def test_chat_endpoint(test_client):
    """Test the chat endpoint."""
    # Create a mock bot with a call method that returns a test response
    mock_chat_engine = MagicMock(spec=ChatEngine)
    mock_chat_engine.process_message.return_value = ChatResponse(
        response="This is a test response",
        conversation_id="test_conversation",
        additional_kwargs={}
    )
    
    # Set the bot on the app state
    test_client.app.state.chat_engine = mock_chat_engine
    
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
    mock_chat_engine.process_message.assert_called_once_with(
        user_input="Hello, test bot!",
        conversation_id="test_conversation"
    )


def test_clear_history_endpoint(test_client):
    """Test the clear history endpoint."""
    # Create a mock bot with a clear_history method
    mock_chat_engine = MagicMock(spec=ChatEngine)
    mock_chat_engine.clear_history.return_value = None
    
    # Set the bot on the app state
    test_client.app.state.chat_engine = mock_chat_engine
    
    # Send a POST request to the clear history endpoint
    response = test_client.post("/api/v1/clear/test_conversation")
    
    # Check that the response is valid
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "History for conversation test_conversation cleared" in data["message"]
    
    # Verify the bot was called with the right parameters
    mock_chat_engine.clear_history.assert_called_once_with(
        conversation_id="test_conversation"
    ) 