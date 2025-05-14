from typing import Optional, Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str = Field(description="User message")
    role: str = Field(description="Message role in conversation")


class MessageTurn(BaseModel):
    human_message: Message = Field(description="Message of human")
    ai_message: Message = Field(description="Message of AI")
    conversation_id: str = Field(description="The id of user in this turn")


class ChatRequest(BaseModel):
    input: str
    conversation_id: Optional[str]


def messages_from_dict(message: dict[str, Any]) -> str:
    human_message_dict: dict[str, str] = message["human_message"]
    ai_message_dict: dict[str, str] = message["ai_message"]

    human_message = Message(message=human_message_dict["message"], role=human_message_dict["role"])
    ai_message = Message(message=ai_message_dict["message"], role=ai_message_dict["role"])
    return f"{human_message.role}: {human_message.message}\n{ai_message.role}: {ai_message.message}"
