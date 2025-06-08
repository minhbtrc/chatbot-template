from typing import Dict, Any

from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    additional_kwargs: Dict[str, Any]