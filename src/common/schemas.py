from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    