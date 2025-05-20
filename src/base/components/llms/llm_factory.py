from src.common.config import Config
from .base import BaseLLMClient

def create_llm_client(config: Config) -> BaseLLMClient:
    """Create a LLM client based on the configuration."""
    if config.model_type == "AZUREOPENAI":
        from src.base.components.llms.variants.azure_openai_client import AzureOpenAIClient
        return AzureOpenAIClient(config)
    elif config.model_type == "OPENAI":
        from src.base.components.llms.variants.openai_client import OpenAIClient
        return OpenAIClient(config)
    elif config.model_type == "VERTEX":
        from src.base.components.llms.variants.vertex_client import VertexAIClient
        return VertexAIClient(config)
    elif config.model_type == "LLAMA":
        from src.base.components.llms.variants.llamacpp_client import LlamaCppClient
        return LlamaCppClient(config)
    else:
        raise ValueError(f"Invalid model type: {config.model_type}")
