from typing import Optional, Dict, Any, List

from langgraph.prebuilt import create_react_agent

from src.common.config import Config
from src.base.components.llms.base import BaseLLMClient
from src.base.components.tools import ToolProvider
from src.base.brains.base import BaseBrain
from src.common.logging import logger


class AgentBrain(BaseBrain):
    def __init__(self, config: Config, llm_client: BaseLLMClient, tool_provider: ToolProvider):
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

    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # If no context is provided, initialize it
        context = context or {}
        
        # Extract conversation history if available
        history = context.get("history", [])
        history = [
            {"role": turn["role"], "content": turn["content"]}
            for turn in history
        ]

        history.append({"role": "user", "content": query})
        response = self.brain.invoke({"messages": history}).get("messages")
        last_message = response[-1]

        return {
            "content": last_message.content,
            "additional_kwargs": last_message.additional_kwargs
        }

    def reset(self) -> None:
        self.brain.clear_cache()
