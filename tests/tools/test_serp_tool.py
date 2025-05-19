"""
Tests for the SERP tool implementation.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.core.components.tools.serp import CustomSearchTool


class TestSerpTool(unittest.TestCase):
    """Test cases for the SERP tool."""
    
    @patch('src.core.components.tools.serp.SerpAPIWrapper')
    def test_initialization(self, mock_serp):
        """Test the SerpTool initialization."""
        # Arrange
        mock_serp_instance = MagicMock()
        mock_serp.return_value = mock_serp_instance
        
        # Act
        tool = CustomSearchTool(api_key="test_key")
        
        # Assert
        self.assertEqual(tool.name, "web_search")
        self.assertIn("current events", tool.description)
        mock_serp.assert_called_once_with(
            params={
                "engine": "google",
                "gl": "us",
                "hl": "en",
            },
            serpapi_api_key="test_key"
        )
    
    @patch('src.core.components.tools.serp.SerpAPIWrapper')
    def test_run(self, mock_serp):
        """Test the run method."""
        # Arrange
        mock_serp_instance = MagicMock()
        mock_serp_instance.run.return_value = "Test search results"
        mock_serp.return_value = mock_serp_instance
        
        tool = CustomSearchTool()
        
        # Act
        result = tool.run("test query")
        
        # Assert
        self.assertEqual(result, "Test search results")
        mock_serp_instance.run.assert_called_once_with("test query")
    
    def test_parameters_schema(self):
        """Test the parameters schema."""
        # Arrange
        with patch('src.core.components.tools.serp.SerpAPIWrapper'):
            tool = CustomSearchTool()
        
        # Act
        schema = tool.get_parameters_schema()
        
        # Assert
        self.assertEqual(schema["type"], "object")
        self.assertIn("query", schema["properties"])
        self.assertEqual(schema["properties"]["query"]["type"], "string")
        self.assertEqual(schema["required"], ["query"])


if __name__ == "__main__":
    unittest.main() 