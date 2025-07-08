#!/usr/bin/env python
"""
RAG Bot CLI – interact with a RAG-powered assistant from your terminal.

Features:
- Load and index a document via `--document`
- Ask questions about the indexed content
- Stream LLM responses if `--stream` is enabled
"""

import argparse
import asyncio
import sys
import colorama
from colorama import Fore, Back, Style

from src.common.config import Config
from src.common.logging import logger
from src.chat_engine import ChatEngine
from src.config_injector import update_injector_with_config, get_instance

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="RAG Bot CLI")
    parser.add_argument(
        "--model",
        type=str,
        help="Model type to use (e.g., OPENAI, AZUREOPENAI)",
    )
    parser.add_argument(
        "--conversation-id",
        type=str,
        default="default",
        help="Conversation ID for the chat session",
    )
    parser.add_argument(
        "--document",
        type=str,
        help="Path to document to process and index",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streamed LLM response",
    )
    return parser


def print_welcome_message():
    """Print welcome message for the CLI."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Welcome to the DeepResearch Bot CLI!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}You can:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Ask questions{Style.RESET_ALL}")
    print(f"{Fore.GREEN}2. Type 'exit' or press Ctrl+C to quit{Style.RESET_ALL}")
    print(f"{Fore.GREEN}3. Type 'clear' to clear conversation history{Style.RESET_ALL}")
    print(f"{Fore.GREEN}4. Type 'help' to show available commands{Style.RESET_ALL}")
    print()


async def process_input_full(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> str:
    """Process user input and return full bot response."""
    if user_input.lower() == "exit":
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    elif user_input.lower() == "clear":
        chat_engine.clear_history(conversation_id, user_id)
        return f"{Fore.GREEN}Conversation history cleared.{Style.RESET_ALL}"
    
    result = await chat_engine.process_message(user_input, conversation_id, user_id)
    return f"{result.response}\n\n{result.additional_kwargs}" if result.additional_kwargs else result.response


async def process_input_stream(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> None:
    """Process user input with streaming response."""
    if user_input.lower() == "exit":
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    elif user_input.lower() == "clear":
        chat_engine.clear_history(conversation_id, user_id)
        print(f"{Fore.GREEN}Conversation history cleared.{Style.RESET_ALL}")
        return

    async for token in chat_engine.stream_process_message(user_input, conversation_id, user_id):
        try:
            print(f"{Fore.BLUE}{token}{Style.RESET_ALL}", end="", flush=True)
        except ValueError:
            pass  # stdout đã đóng
    # print()  # newline after stream ends


async def main():
    """Run the DeepResearch Bot CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    config = Config(expert_type="DEEPRESEARCH")
    if args.model:
        config.model_type = args.model.upper()

    update_injector_with_config(config)

    logger.info(f"{Fore.MAGENTA}Starting DeepResearch Bot CLI with model: {config.model_type}{Style.RESET_ALL}")

    chat_engine: ChatEngine = get_instance(ChatEngine)
    user_id = "default"

    print_welcome_message()

    try:
        while True:
            print(f"{Fore.YELLOW}User:{Style.RESET_ALL} ", end="", flush=True)
            user_input = input()
            print(f"{Fore.CYAN}Bot:{Style.RESET_ALL} ", end="", flush=True)

            if args.stream:
                await process_input_stream(chat_engine, user_input, args.conversation_id, user_id)
            else:
                response = await process_input_full(chat_engine, user_input, args.conversation_id, user_id)
                try:
                    print(response)
                except (ValueError, OSError):
                    break  # stdout đã đóng, dừng chương trình

            print()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        try:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        except Exception:
            pass
    finally:
        try:
            chat_engine.close()
        except Exception:
            pass
        import logging
        logging.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
