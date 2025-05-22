import argparse
import asyncio
import sys

from src.common.config import Config
from src.common.logging import logger
from src.experts.rag_bot.expert import RAGBotExpert
from src.chat_engine import ChatEngine
from src.config_injector import update_injector_with_config, get_instance


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
    return parser


def print_welcome_message():
    """Print welcome message for the CLI."""
    print("\nWelcome to the RAG Bot CLI!")
    print("You can:")
    print("1. Process documents using --document <path>")
    print("2. Ask questions about your documents")
    print("3. Type 'exit' or press Ctrl+C to quit")
    print("4. Type 'clear' to clear conversation history")
    print()


async def process_input(rag_bot: RAGBotExpert, chat_engine: ChatEngine, user_input: str, conversation_id: str) -> str:
    """Process user input and return bot response."""
    if user_input.lower() == "exit":
        print("\nGoodbye!")
        sys.exit(0)
    elif user_input.lower() == "clear":
        chat_engine.clear_history(conversation_id)
        return "Conversation history cleared."
    
    response = await rag_bot.aprocess(user_input, conversation_id)
    return response.response


async def main():
    """Run the RAG Bot CLI application."""
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Create configuration
    config = Config()
    print(f"77777{config.brain_type}")
    
    # Update config based on CLI arguments
    if args.model:
        config.model_type = args.model.upper()
    
    update_injector_with_config(config)
    
    logger.info(f"Starting RAG Bot CLI with model: {config.model_type}")
    
    # Get instances
    rag_bot = get_instance(RAGBotExpert)
    chat_engine = get_instance(ChatEngine)
    
    # Process document if provided
    if args.document:
        print(f"\nProcessing document: {args.document}")
        rag_bot.process_document(args.document)
        print("Document processed and indexed successfully!")
    
    # Print welcome message
    print_welcome_message()
    
    # Main interaction loop
    try:
        while True:
            # Get user input
            user_input = input("User: ")
            
            # Process input and get response
            response = await process_input(rag_bot, chat_engine, user_input, args.conversation_id)
            
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