#!/usr/bin/env python
"""
Command Line Interface for quick local testing of the chatbot.

This script allows users to interact with the chatbot directly from the command line,
without needing to run the API server.

Usage:
    python cli.py

Exit the chat by typing 'exit', 'quit', or pressing Ctrl+C.
"""

import argparse
import sys
from typing import Optional, cast

from src.bot import Bot
from src.common.config import Config
from src.common.logging import logger
from dependency_injector import get_instance, update_injector_with_config


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Command Line Interface for the chatbot"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="openai",
        choices=["openai", "llama", "azureopenai"],
        help="Model type to use (default: openai)",
    )
    parser.add_argument(
        "--conversation-id",
        type=str,
        default="cli_session",
        help="Conversation ID for the session (default: cli_session)",
    )
    return parser


def print_welcome_message():
    """Print welcome message and instructions."""
    print("\n=== Chatbot CLI ===")
    print("Type 'exit' or 'quit' to exit the chat.")
    print("Press Ctrl+C to exit at any time.")
    print("=" * 20)
    print()


def process_input(bot: Bot, user_input: str, conversation_id: str) -> Optional[str]:
    """Process user input and return bot response."""
    # Check for exit commands
    if user_input.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        sys.exit(0)
        
    # Process the message
    result = bot.call(user_input, conversation_id)
    return result["response"]


def main():
    """Run the CLI application."""
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Create configuration
    config = Config()
    
    # Update config based on CLI arguments
    if args.model:
        config.model_type = args.model.upper()
    
    update_injector_with_config(config)
    
    logger.info(f"Starting CLI with model: {config.model_type}")
    
    # Create the bot with the brain and memory
    bot = cast(Bot, get_instance(Bot))
    
    # Print welcome message
    print_welcome_message()
    
    # Main interaction loop
    try:
        while True:
            # Get user input
            user_input = input("User: ")
            
            # Process input and get response
            response = process_input(bot, user_input, args.conversation_id)
            
            # Print the response
            print(f"Bot: {response}")
            print()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in CLI: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 