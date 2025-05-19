from src.common.config import Config
from src.core.brains.services.agent_brain import AgentBrain
from src.core.brains.services.llm_brain import LLMBrain
from src.core.brains.base import BaseBrain
from src.core.components.llms.base import BaseLLMClient
from src.core.components.tools import ToolProvider

def create_brain(config: Config, llm_client: BaseLLMClient, tool_provider: ToolProvider) -> BaseBrain:
    if config.brain_type and config.brain_type.upper() == "AGENT":
        return AgentBrain(config, llm_client, tool_provider)
    else:
        return LLMBrain(config, llm_client)
