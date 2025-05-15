"""
Common data models for the application.

This module contains Pydantic models used throughout the application.
"""

from typing import Dict, Any, TypedDict

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Model for a message in a conversation."""
    message: str = Field(description="Message content")
    role: str = Field(description="Message role in conversation (user, assistant, system)")


class MessageTurn(BaseModel):
    """Model for a turn in a conversation (user message and AI response)."""
    human_message: Message = Field(description="Message from human")
    ai_message: Message = Field(description="Message from AI")
    conversation_id: str = Field(description="The ID of the conversation for this turn")


class Tool(BaseModel):
    """Model for a tool that can be used by the AI."""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: Dict[str, Any] = Field(description="Tool parameters schema")


class MessageDict(TypedDict):
    """Type definition for message dictionary structure."""
    human_message: Dict[str, str]
    ai_message: Dict[str, str]


def messages_from_dict(message: MessageDict) -> str:
    """Convert a message dictionary to a formatted string.
    
    Args:
        message: Dictionary containing human_message and ai_message
        
    Returns:
        Formatted message string
    """
    human_message_dict = message["human_message"]
    ai_message_dict = message["ai_message"]

    human_message = Message(message=human_message_dict["message"], role=human_message_dict["role"])
    ai_message = Message(message=ai_message_dict["message"], role=ai_message_dict["role"])
    
    return f"{human_message.role}: {human_message.message}\n{ai_message.role}: {ai_message.message}" 