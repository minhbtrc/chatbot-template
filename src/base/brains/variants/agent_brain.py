from typing import Optional, Dict, Any, List, Generator, AsyncGenerator

from langgraph.prebuilt import create_react_agent

from src.common.config import Config
from src.base.components import LLMInterface, ToolProvider
from src.base.brains.base import BaseBrain
from src.common.logging import logger


class AgentBrain(BaseBrain):
    def __init__(self, config: Config, llm_client: LLMInterface, tool_provider: ToolProvider):
        self.config = config
        self.tool_provider = tool_provider
        self.llm_client = llm_client
                
        # Configure the brain with tools from the provider if available
        self.brain = create_react_agent(
            model=self.llm_client.client,
            tools=tool_provider.get_langchain_tools()
        )

    def use_tools(self, tools: Optional[List[Any]] = None) -> None:
        logger.info("Tools are already added in brain")

    def _build_messages(self, history: List[Dict[str, Any]], system_message: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Build the messages for the agent.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
        
        Returns:
            List of messages
        """
        messages: List[Dict[str, Any]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.extend(history)
        return messages

    def think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the input query and return a response.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
        
        Returns:
            Dictionary containing the response
        """
        messages = self._build_messages(history, system_message)
        response = self.brain.invoke({"messages": messages}).get("messages")
        last_message = response[-1]

        return {
            "content": last_message.content,
            "additional_kwargs": last_message.additional_kwargs
        }
    
    async def athink(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Process the input query and return a response asynchronously.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
        
        Returns:
            Dictionary containing the response
        """
        messages = self._build_messages(history, system_message)
        response = await self.brain.ainvoke({"messages": messages})
        last_message = response.get("messages")[-1]

        return {
            "content": last_message.content,
            "additional_kwargs": last_message.additional_kwargs
        }
    
    def stream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> Generator[str, None, None]:
        """
        Process the input query and stream the response.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
        
        """
        messages = self._build_messages(history, system_message)
        response = self.brain.stream({"messages": messages})
        for chunk in response:
            yield chunk.content

    async def astream_think(self, history: List[Dict[str, Any]], system_message: Optional[str] = None, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Process the input query and stream the response asynchronously.
        
        Args:
            history: List of messages in the conversation
            system_message: Optional system message for the brain
        
        """
        messages = self._build_messages(history, system_message)
        response = await self.brain.astream({"messages": messages})
        async for chunk in response:
            yield chunk.content

    def reset(self) -> None:
        self.brain.clear_cache()
