"""API models for chatbot requests and responses."""
from typing import Optional, Dict, Any

from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model."""
    
    input: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID (optional, will be auto-generated if not provided)")


class ChatResponse(BaseModel):
    """Chat response model."""
    
    output: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    additional_kwargs: Dict[str, Any] = Field(..., description="Additional kwargs")


class StreamingChatChunk(BaseModel):
    """Streaming chat chunk model for Server-Sent Events."""
    
    type: str = Field(..., description="Type of chunk: 'start', 'chunk', 'end', or 'error'")
    content: Optional[str] = Field(default=None, description="Content chunk (for 'chunk' type)")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    error: Optional[str] = Field(default=None, description="Error message (for 'error' type)")
    timestamp: Optional[str] = Field(default=None, description="Timestamp of the chunk")


class RagDocumentRequest(BaseModel):
    """RAG document request model."""
    
    file: UploadFile = File(...)
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
