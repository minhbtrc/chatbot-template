"""
Tests for the base tool implementation.
"""

import unittest
from typing import Dict

from src.core.components.tools import SimpleTool


class TestBaseTool(unittest.TestCase):
    """Test cases for the BaseTool class and implementations."""
    
    def test_simple_tool(self):
        """Test the SimpleTool implementation."""
        # Create a simple function
        def add_numbers(input_data: Dict[str, int]) -> int:
            return input_data.get("a", 0) + input_data.get("b", 0)
        
        # Create parameters schema
        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        }
        
        # Create a SimpleTool
        tool = SimpleTool(
            name="add_numbers",
            description="Add two numbers together",
            func=add_numbers,
            parameters_schema=schema
        )
        
        # Test the tool execution
        result = tool.run({"a": 2, "b": 3})
        self.assertEqual(result, 5)
        
        # Test the schema
        tool_schema = tool.get_parameters_schema()
        self.assertEqual(tool_schema, schema)
        
        # Test OpenAI format
        openai_tool = tool.to_openai_tool()
        self.assertEqual(openai_tool["type"], "function")
        self.assertEqual(openai_tool["function"]["name"], "add_numbers")
        self.assertEqual(openai_tool["function"]["description"], "Add two numbers together")
        self.assertEqual(openai_tool["function"]["parameters"], schema)


if __name__ == "__main__":
    unittest.main() 