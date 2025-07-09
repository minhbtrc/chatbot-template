import argparse
import asyncio
import sys
import colorama
from colorama import Fore, Style
from typing import Optional, cast

from src.common.config import Config
from src.common.logging import logger
from src.experts.rag_bot.expert import RAGBotExpert
from src.chat_engine import ChatEngine
from src.config_injector import update_injector_with_config, get_instance

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Unified Bot CLI - choose your bot mode and start chatting"
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["qna", "rag", "deepresearch"],
        help="Bot mode to use: qna (basic Q&A), rag (document-aware), deepresearch (advanced research)",
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
        "--document",
        type=str,
        help="Path to document to process and index (RAG mode only)",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streamed LLM response (default: off)",
    )
    return parser


def print_welcome_message(mode: str):
    """Print welcome message based on the selected mode."""
    mode_info = {
        "qna": {
            "title": "QNA Bot CLI",
            "description": "Basic question-answering chatbot"
        },
        "rag": {
            "title": "RAG Bot CLI", 
            "description": "RAG-powered assistant with document processing"
        },
        "deepresearch": {
            "title": "DeepResearch Bot CLI",
            "description": "Advanced research assistant"
        }
    }
    
    info = mode_info[mode]
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== {info['title']} ==={Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{info['description']}{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}• Type your questions or messages{Style.RESET_ALL}")
    print(f"{Fore.GREEN}• Type 'exit' or 'quit' to exit{Style.RESET_ALL}")
    print(f"{Fore.GREEN}• Press Ctrl+C to exit at any time{Style.RESET_ALL}")
    print(f"{Fore.GREEN}• Type 'clear' to clear conversation history{Style.RESET_ALL}")
    
    if mode == "rag":
        print(f"{Fore.GREEN}• Use --document <path> to process documents{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
    print()


async def process_streaming(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> None:
    """Stream bot response token by token."""
    if user_input.lower() in ["exit", "quit"]:
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    elif user_input.lower() == "clear":
        chat_engine.clear_history(conversation_id, user_id)
        print(f"{Fore.GREEN}Conversation history cleared.{Style.RESET_ALL}")
        return

    try:
        async for token in chat_engine.stream_process_message(user_input, conversation_id, user_id):
            print(f"{Fore.BLUE}{token}{Style.RESET_ALL}", end="", flush=True)
        print()  # newline after stream ends
    except ValueError:
        pass  # stdout closed


async def process_input(
    chat_engine: ChatEngine,
    user_input: str,
    conversation_id: str,
    user_id: str
) -> Optional[str]:
    """Return full bot response."""
    if user_input.lower() in ["exit", "quit"]:
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    elif user_input.lower() == "clear":
        chat_engine.clear_history(conversation_id, user_id)
        return f"{Fore.GREEN}Conversation history cleared.{Style.RESET_ALL}"
    
    result = await chat_engine.process_message(user_input, conversation_id, user_id)
    return f"{result.response}\n\n{result.additional_kwargs}" if result.additional_kwargs else result.response


def get_expert_type(mode: str) -> str:
    """Get the expert type based on the mode."""
    mode_to_expert = {
        "qna": "QNA",
        "rag": "RAG", 
        "deepresearch": "DEEPRESEARCH"
    }
    return mode_to_expert[mode]


async def process_document_if_needed(mode: str, document_path: Optional[str], conversation_id: str, user_id: str):
    """Process document for RAG mode if document path is provided."""
    if mode == "rag" and document_path:
        print(f"\n{Fore.YELLOW}Processing document: {document_path}{Style.RESET_ALL}")
        try:
            rag_bot = cast(RAGBotExpert, get_instance(RAGBotExpert))
            await rag_bot.aprocess_document(document_path, user_id, conversation_id)
            print(f"{Fore.GREEN}Document processed and indexed successfully!{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.RED}Error processing document: {e}{Style.RESET_ALL}\n")


async def main():
    """Run the unified CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    if args.document and args.mode != "rag":
        print(f"{Fore.RED}Error: --document can only be used with --mode rag{Style.RESET_ALL}")
        sys.exit(1)

    # Setup configuration
    expert_type = get_expert_type(args.mode)
    config = Config(expert_type=expert_type)
    if args.model:
        config.model_type = args.model.upper()

    update_injector_with_config(config)

    logger.info(f"{Fore.MAGENTA}Starting {args.mode.upper()} Bot CLI with model: {config.model_type}{Style.RESET_ALL}")
    
    # Initialize chat engine
    chat_engine = cast(ChatEngine, get_instance(ChatEngine))
    user_id = "default"

    # Process document if needed (RAG mode)
    await process_document_if_needed(args.mode, args.document, args.conversation_id, user_id)

    # Print welcome message
    print_welcome_message(args.mode)

    try:
        while True:
            print(f"{Fore.YELLOW}User:{Style.RESET_ALL} ", end="", flush=True)
            user_input = input()
            
            if not user_input.strip():
                continue
                
            print(f"{Fore.CYAN}Bot:{Style.RESET_ALL} ", end="", flush=True)
            
            if args.stream:
                await process_streaming(chat_engine, user_input, args.conversation_id, user_id)
            else:
                response = await process_input(chat_engine, user_input, args.conversation_id, user_id)
                if response:
                    try:
                        print(response)
                    except (ValueError, OSError):
                        break  # stdout closed, stop program
            print()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Error in CLI: {e}")
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
