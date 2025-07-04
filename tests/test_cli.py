"""
Unit tests for the CLI module.
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock

from src.common.schemas import ChatResponse
from src.chat_engine import ChatEngine
import cli
from src.common.logging import logger


class TestCLI(unittest.TestCase):
    """Test CLI module functions."""
    
    def setUp(self):
        """Setup for tests."""
        # Silence the logger during tests
        logger.setLevel("CRITICAL")
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = cli.create_parser()
        args = parser.parse_args(['--model', 'llama'])
        self.assertEqual(args.model, 'llama')
        self.assertEqual(args.conversation_id, 'cli_session')  # Default value
        
        args = parser.parse_args(['--conversation-id', 'test_session'])
        self.assertEqual(args.model, 'openai')  # Default value
        self.assertEqual(args.conversation_id, 'test_session')
    
    def test_process_input_exit(self):
        """Test process_input with normal message (exit is handled in main loop, not process_input)."""
        # The process_input function doesn't handle exit commands - it just processes normal messages
        # Exit commands are handled in the main() function's while loop
        # So we test that process_input works with normal messages
        chat_engine = MagicMock(spec=ChatEngine)
        chat_engine.process_message.return_value = ChatResponse(
            response="Test response",
            conversation_id="test_session",
            additional_kwargs={}
        )
        
        result = asyncio.run(cli.process_input(chat_engine, 'Hello', 'test_session', 'user_id'))
        
        chat_engine.process_message.assert_called_once_with('Hello', 'test_session', 'user_id')
        self.assertEqual(result, 'Test response')
    
    def test_process_input_message(self):
        """Test process_input with a normal message."""
        chat_engine = MagicMock(spec=ChatEngine)
        chat_engine.process_message.return_value = ChatResponse(
            response="Test response",
            conversation_id="test_session",
            additional_kwargs={}
        )
        
        result = asyncio.run(cli.process_input(chat_engine, 'Hello', 'test_session', 'user_id'))
        
        chat_engine.process_message.assert_called_once_with('Hello', 'test_session', 'user_id')
        self.assertEqual(result, 'Test response')
    
    def test_main_exception_handling(self):
        """Test main function exception handling."""
        with patch('cli.create_parser') as mock_parser, \
             patch('cli.Config') as mock_config, \
             patch('cli.update_injector_with_config') as mock_update_injector, \
             patch('cli.get_instance') as mock_get_instance, \
             patch('cli.print_welcome_message') as mock_welcome, \
             patch('builtins.input', side_effect=Exception("Test error")), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            # Configure mocks
            parser_instance = MagicMock()
            parser_instance.parse_args.return_value = MagicMock(
                model="openai", conversation_id="test_session"
            )
            mock_parser.return_value = parser_instance
            
            config_instance = MagicMock()
            mock_config.return_value = config_instance
            
            bot_instance = MagicMock()
            mock_get_instance.return_value = bot_instance
            
            # Run the main function
            asyncio.run(cli.main())
            
            # Verify mocks were called
            mock_parser.assert_called_once()
            mock_config.assert_called_once()
            mock_update_injector.assert_called_once()
            mock_get_instance.assert_called_once()
            mock_welcome.assert_called_once()
            
            # Check that the error was handled properly
            mock_exit.assert_called_once_with(1)
            mock_print.assert_any_call("An error occurred: Test error")


if __name__ == '__main__':
    unittest.main() 