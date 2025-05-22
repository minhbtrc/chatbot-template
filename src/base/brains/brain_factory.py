from src.common.config import Config
from src.base.components import LLMInterface, ToolProvider
from .base import BaseBrain
from .variants.agent_brain import AgentBrain
from .variants.llm_brain import LLMBrain

def create_brain(config: Config, llm_client: LLMInterface, tool_provider: ToolProvider) -> BaseBrain:
    if config.brain_type and config.brain_type.upper() == "AGENT":
        return AgentBrain(config, llm_client, tool_provider)
    else:
        return LLMBrain(config, llm_client)
