from typing import Dict, Any, List, Optional, Generator, AsyncGenerator

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from src.base.components.llms.base import BaseLLMClient
from src.common.config import Config
from src.common.logging import logger


class GeminiClient(BaseLLMClient):
    """
    Gemini client implementation.
    """
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.gemini_api_key
        self.model_name = config.gemini_model_name or "gemini-pro"
        
        if not self.api_key:
            raise ValueError("Gemini API Key is required")
            
        self.client = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            convert_system_message_to_human=True
        )

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[BaseMessage]:
        """Convert dictionary messages to LangChain messages."""
        converted_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                converted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                converted_messages.append(AIMessage(content=content))
            elif role == "system":
                converted_messages.append(SystemMessage(content=content))
        return converted_messages

    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        Chat with the model.
        """
        langchain_messages = self._convert_messages(messages)
        response = self.client.invoke(langchain_messages, **kwargs)
        return {
            "role": "assistant",
            "content": response.content
        }

    async def achat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        Async chat with the model.
        """
        langchain_messages = self._convert_messages(messages)
        response = await self.client.ainvoke(langchain_messages, **kwargs)
        return {
            "role": "assistant",
            "content": response.content
        }

    def stream_chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Generator[str, None, None]:
        """
        Stream chat with the model.
        """
        langchain_messages = self._convert_messages(messages)
        for chunk in self.client.stream(langchain_messages, **kwargs):
            if chunk.content:
                yield chunk.content

    async def astream_chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Async stream chat with the model.
        """
        langchain_messages = self._convert_messages(messages)
        async for chunk in self.client.astream(langchain_messages, **kwargs):
            if chunk.content:
                yield chunk.content

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "type": "gemini",
            "model": self.model_name
        }
