from typing import Dict, Any, Optional

from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    session_id: Optional[str] = None
    additional_kwargs: Dict[str, Any]