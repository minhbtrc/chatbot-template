"""
SQL memory implementation using repository pattern.
"""

from typing import Dict, List, Any, Optional

from src.base.components.memories.base import BaseChatbotMemory
from src.database import get_database, ConversationMessageRepository
from src.common.logging import logger


class SQLMemory(BaseChatbotMemory):
    """
    SQL-based memory implementation using repository pattern.
    
    This implementation stores all messages in a SQL database using SQLAlchemy.
    """
    
    def __init__(self, user_id: Optional[int] = None):
        """
        Initialize the SQL memory.
        
        Args:
            user_id: Optional user ID to associate messages with
        """
        self.user_id = user_id
        self.db = get_database()
        self._conversation_cache: Dict[str, List[Dict[str, Any]]] = {}
        logger.info(f"Initialized SQLMemory with user_id: {user_id}")
    
    def _get_repository(self) -> ConversationMessageRepository:
        """Get a conversation message repository with a new session."""
        session = self.db.get_session()
        return ConversationMessageRepository(session)
    
    def _add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            message: Message dictionary containing role, content, conversation_id, timestamp
        """
        repo = self._get_repository()
        try:
            # Extract user_id from conversation_id if not set and conversation_id has user prefix
            user_id = self.user_id
            if not user_id and message["conversation_id"].startswith("user_"):
                try:
                    # Extract user_id from conversation_id format: user_{user_id}_conv_{conv_id}
                    parts = message["conversation_id"].split("_")
                    if len(parts) >= 2 and parts[0] == "user":
                        user_id = int(parts[1])
                except (ValueError, IndexError):
                    logger.warning(f"Could not extract user_id from conversation_id: {message['conversation_id']}")
            
            repo.add_message(
                conversation_id=message["conversation_id"],
                role=message["role"],
                content=message["content"],
                user_id=user_id,
                metadata=message.get("metadata")
            )
            
            # Clear cache for this conversation
            if message["conversation_id"] in self._conversation_cache:
                del self._conversation_cache[message["conversation_id"]]
            
            logger.debug(f"Added message to conversation {message['conversation_id']}")
            
        except Exception as e:
            logger.error(f"Error adding message to SQL memory: {str(e)}")
            raise
        finally:
            # Close the session
            repo.session.close()
    
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        # Check cache first
        if conversation_id in self._conversation_cache:
            return self._conversation_cache[conversation_id]
        
        repo = self._get_repository()
        try:
            messages = repo.get_conversation_history_dict(conversation_id)
            
            # Format for the brain (only include role and content)
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
            
            # Cache the result
            self._conversation_cache[conversation_id] = formatted_messages
            
            logger.debug(f"Retrieved {len(formatted_messages)} messages for conversation {conversation_id}")
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error getting history from SQL memory: {str(e)}")
            return []
        finally:
            # Close the session
            repo.session.close()
    
    def clear_history(self, conversation_id: str) -> None:
        """
        Clear the conversation history.
        
        Args:
            conversation_id: ID of the conversation to clear
        """
        repo = self._get_repository()
        try:
            deleted_count = repo.clear_conversation_history(conversation_id)
            
            # Clear cache for this conversation
            if conversation_id in self._conversation_cache:
                del self._conversation_cache[conversation_id]
            
            logger.info(f"Cleared {deleted_count} messages from conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error clearing history from SQL memory: {str(e)}")
            raise
        finally:
            # Close the session
            repo.session.close()
    
    def get_all_conversations(self) -> List[str]:
        """
        Get all conversation IDs.
        
        Returns:
            List of conversation IDs
        """
        repo = self._get_repository()
        try:
            conversation_ids = repo.get_all_conversation_ids(self.user_id)
            
            logger.debug(f"Retrieved {len(conversation_ids)} conversation IDs")
            return conversation_ids
            
        except Exception as e:
            logger.error(f"Error getting conversations from SQL memory: {str(e)}")
            return []
        finally:
            # Close the session
            repo.session.close()
    
    def get_user_conversations(self, user_id: int) -> List[str]:
        """
        Get all conversation IDs for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversation IDs belonging to the user
        """
        repo = self._get_repository()
        try:
            conversation_ids = repo.get_user_conversations(user_id)
            
            logger.debug(f"Retrieved {len(conversation_ids)} conversations for user {user_id}")
            return conversation_ids
            
        except Exception as e:
            logger.error(f"Error getting user conversations from SQL memory: {str(e)}")
            return []
        finally:
            # Close the session
            repo.session.close()
    
    def close(self) -> None:
        """Close the memory."""
        # Clear cache
        self._conversation_cache.clear()
        logger.info("SQLMemory closed successfully") 