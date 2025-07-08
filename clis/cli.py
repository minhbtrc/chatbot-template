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
import colorama
from colorama import Fore, Back, Style
from typing import Optional, cast

from src.chat_engine import ChatEngine
from src.common.config import Config
from src.common.logging import logger
from src.config_injector import get_instance, update_injector_with_config

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)


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
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streamed LLM response (default: off)",
    )
    return parser


def print_welcome_message():
    """Print welcome message and instructions."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Chatbot CLI ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'exit' or 'quit' to exit the chat.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Press Ctrl+C to exit at any time.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 20}{Style.RESET_ALL}")
    print()


async def process_streaming(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> None:
    """Stream bot response token by token."""
    async for token in chat_engine.stream_process_message(user_input, conversation_id, user_id):
        print(f"{Fore.BLUE}{token}{Style.RESET_ALL}", end="", flush=True)
    print()  # newline after stream ends


async def process_input(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> Optional[str]:
    """Return full bot response."""
    result = await chat_engine.process_message(user_input, conversation_id, user_id)
    return f"{result.response}\n\n{result.additional_kwargs}" if result.additional_kwargs else result.response


async def main():
    """Run the CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    config = Config(expert_type="QNA")
    if args.model:
        config.model_type = args.model.upper()

    update_injector_with_config(config)

    logger.info(f"{Fore.MAGENTA}Starting CLI with model: {config.model_type}{Style.RESET_ALL}")
    chat_engine = cast(ChatEngine, get_instance(ChatEngine))

    print_welcome_message()

    user_id = "default"
    try:
        while True:
            print(f"{Fore.YELLOW}User:{Style.RESET_ALL} ", end="", flush=True)
            user_input = input()
            if user_input.strip().lower() in ["exit", "quit"]:
                print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
                break

            print(f"{Fore.CYAN}Bot:{Style.RESET_ALL} ", end="", flush=True)
            if args.stream:
                await process_streaming(chat_engine, user_input, args.conversation_id, user_id)
            else:
                response = await process_input(chat_engine, user_input, args.conversation_id, user_id)
                print(response)
            print()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in CLI: {e}")
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        sys.exit(1)
    finally:
        chat_engine.close()

if __name__ == "__main__":
    asyncio.run(main())
