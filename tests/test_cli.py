"""
Unit tests for the CLI module.
"""

import unittest
from unittest.mock import patch, MagicMock

import cli
from src.bot import Bot
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
        """Test process_input with exit command."""
        bot = MagicMock(spec=Bot)
        
        with patch('sys.exit') as mock_exit:
            cli.process_input(bot, 'exit', 'test_session')
            mock_exit.assert_called_once_with(0)
            
        with patch('sys.exit') as mock_exit:
            cli.process_input(bot, 'quit', 'test_session')
            mock_exit.assert_called_once_with(0)
    
    def test_process_input_message(self):
        """Test process_input with a normal message."""
        bot = MagicMock(spec=Bot)
        bot.call.return_value = {"response": "Test response", "conversation_id": "test_session"}
        
        result = cli.process_input(bot, 'Hello', 'test_session')
        
        bot.call.assert_called_once_with('Hello', 'test_session')
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
            cli.main()
            
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