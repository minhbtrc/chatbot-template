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
import asyncio
from typing import Optional, cast

from src.chat_engine import ChatEngine
from src.common.config import Config
from src.common.logging import logger
from src.config_injector import get_instance, update_injector_with_config


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


async def process_input(chat_engine: ChatEngine, user_input: str, conversation_id: str) -> Optional[str]:
    """Process user input and return bot response."""
    # Check for exit commands
    if user_input.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        chat_engine.close()
        sys.exit(0)
        
    # Process the message
    result = await chat_engine.process_message(user_input, conversation_id)
    return f"{result.response}\n\n{result.additional_kwargs}" if result.additional_kwargs else result.response

async def main():
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
    chat_engine = cast(ChatEngine, get_instance(ChatEngine))
    
    # Print welcome message
    print_welcome_message()
    
    # Main interaction loop
    try:
        while True:
            # Get user input
            user_input = input("User: ")
            
            # Process input and get response
            response = await process_input(chat_engine, user_input, args.conversation_id)
            
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
    finally:
        chat_engine.close()


if __name__ == "__main__":
    asyncio.run(main()) 