"""
Tests for the base LLM client implementation.
"""

import unittest
from typing import Dict, Any, List

from src.core.components.tools.base import BaseTool
from src.core.components.llms import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Mock implementation of BaseLLMClient for testing."""

    def __init__(self):
        """Initialize the mock client."""
        self.chat_called = False
        self.complete_called = False
        self.model_info_called = False
        self.close_called = False
        
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Mock implementation of chat method."""
        self.chat_called = True
        self.chat_messages = messages
        self.chat_kwargs = kwargs
        return "This is a mock response"
        
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Mock implementation of complete method."""
        self.complete_called = True
        self.complete_prompt = prompt
        self.complete_kwargs = kwargs
        return "This is a mock completion"
        
    def get_model_info(self) -> Dict[str, Any]:
        """Mock implementation of get_model_info method."""
        self.model_info_called = True
        return {"provider": "Mock", "model": "mock-model"}
        
    def close(self) -> None:
        """Mock implementation of close method."""
        self.close_called = True

    def bind_tools(self, tools: List[BaseTool]) -> None:
        """Mock implementation of bind_tools method."""
        self.tools = tools


class TestBaseLLMClient(unittest.TestCase):
    """Test cases for the BaseLLMClient implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = MockLLMClient()
        
    def test_chat(self):
        """Test the chat method."""
        messages = [{"role": "user", "content": "Hello"}]
        kwargs = {"temperature": 0.7}
        response = self.client.chat(messages, **kwargs)
        
        self.assertTrue(self.client.chat_called)
        self.assertEqual(self.client.chat_messages, messages)
        self.assertEqual(self.client.chat_kwargs, {"temperature": 0.7})
        self.assertEqual(response, "This is a mock response")
        
    def test_complete(self):
        """Test the complete method."""
        prompt = "Tell me a story"
        kwargs = {"max_tokens": 100}
        response = self.client.complete(prompt, **kwargs)
        
        self.assertTrue(self.client.complete_called)
        self.assertEqual(self.client.complete_prompt, prompt)
        self.assertEqual(self.client.complete_kwargs, {"max_tokens": 100})
        self.assertEqual(response, "This is a mock completion")
        
    def test_get_model_info(self):
        """Test the get_model_info method."""
        info = self.client.get_model_info()
        
        self.assertTrue(self.client.model_info_called)
        self.assertEqual(info["provider"], "Mock")
        self.assertEqual(info["model"], "mock-model")
        
    def test_close(self):
        """Test the close method."""
        self.client.close()
        self.assertTrue(self.client.close_called)


if __name__ == "__main__":
    unittest.main() 