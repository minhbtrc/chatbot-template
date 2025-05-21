from src.common.config import Config
from .base import BaseLLMClient

def create_llm_client(config: Config) -> BaseLLMClient:
    """Create a LLM client based on the configuration."""
    model_type = config.model_type.upper() if config.model_type else None
    if model_type == "AZUREOPENAI":
        from src.base.components.llms.variants.azure_openai_client import AzureOpenAIClient
        return AzureOpenAIClient(config)
    elif model_type == "OPENAI":
        from src.base.components.llms.variants.openai_client import OpenAIClient
        return OpenAIClient(config)
    elif model_type == "VERTEX":
        from src.base.components.llms.variants.vertex_client import VertexAIClient
        return VertexAIClient(config)
    elif model_type == "LLAMA":
        from src.base.components.llms.variants.llamacpp_client import LlamaCppClient
        return LlamaCppClient(config)
    else:
        raise ValueError(f"Invalid model type: {model_type}")
