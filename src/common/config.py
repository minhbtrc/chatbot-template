"""
Configuration management for the application.
"""

import json
import os
from typing import Optional, Any

from dotenv import load_dotenv
load_dotenv()

from pydantic import Field, model_validator, BaseModel


class Config(BaseModel):
    """Application settings loaded from environment variables."""
    # Bot Configuration
    system_message: Optional[str] = Field(default=None, description="System message to use in chat prompts")
    ai_prefix: Optional[str] = Field(default="assistant", description="Prefix for AI messages in the prompt")
    human_prefix: Optional[str] = Field(default="user", description="Prefix for human messages in the prompt")
    memory_key: Optional[str] = Field(default="history", description="Key to use for conversation history")
    
    # Chat Configuration
    model_type: str = Field(default="OPENAI", description="The type of model to use (OPENAI, VERTEX, LLAMA, AZUREOPENAI)")
    
    ## Azure OpenAI Configuration
    azure_chat_model_key: Optional[str] = Field(default=None, description="Azure OpenAI API Key")
    azure_chat_model_version: Optional[str] = Field(default=None, description="Azure OpenAI API Version")
    azure_chat_model_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI Endpoint URL")
    azure_chat_model_deployment: Optional[str] = Field(default=None, description="Azure OpenAI Deployment Name")

    ## OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    base_model_name: Optional[str] = Field(default=None, description="Base model name to use")

    ## LlamaCpp Configuration
    model_path: Optional[str] = Field(default=None, description="Path to LlamaCpp model")

    ## Vertex AI Configuration
    credentials: Optional[str] = Field(default=None, description="Path to Vertex AI credentials file")

    # Memory Configuration
    bot_memory_type: Optional[str] = Field(default="inmemory", description="Type of memory to use (inmemory, mongodb)")
    memory_window_size: int = Field(default=5, description="Number of messages to include in the context window")

    ## Memory-MongoDB Configuration
    mongo_uri: Optional[str] = Field(default=None, description="MongoDB connection string")
    mongo_username: Optional[str] = Field(default=None, description="MongoDB username")
    mongo_password: Optional[str] = Field(default=None, description="MongoDB password")
    mongo_database: Optional[str] = Field(default=None, description="MongoDB database name")
    mongo_collection: Optional[str] = Field(default=None, description="MongoDB collection name")
    mongo_cluster: Optional[str] = Field(default=None, description="MongoDB cluster")

    # Server Configuration
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")

    ## Brain Configuration
    brain_type: Optional[str] = Field(default="AGENT", description="Type of brain to use (AGENT, LLM)")

    ## Bot Configuration
    bot_type: Optional[str] = Field(default="CHAT", description="Type of bot to use (CHAT, RAG, DEEPRESEARCH)")

    # Vector Database Configuration
    vector_database_type: Optional[str] = Field(default="CHROMA", description="Type of vector database to use (CHROMA, FAISS)")
    vector_database_chroma_path: Optional[str] = Field(default="./chroma_db", description="Path to Chroma vector database")

    # Embedding Configuration
    embedding_type: Optional[str] = Field(default="AZUREOPENAI", description="Type of embedding to use (OPENAI, AZUREOPENAI)")

    ## Embedding-OpenAI Configuration
    openai_embedding_model: Optional[str] = Field(default="text-embedding-3-small", description="OpenAI embedding model to use")

    ## Embedding-AzureOpenAI Configuration
    azure_embedding_model_deployment: Optional[str] = Field(default=None, description="Azure OpenAI embedding model deployment")
    azure_embedding_model_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI embedding model endpoint")
    azure_embedding_model_key: Optional[str] = Field(default=None, description="Azure OpenAI embedding model key")
    azure_embedding_model_version: Optional[str] = Field(default=None, description="Azure OpenAI embedding model version")

    # Tracing Configuration
    enable_langfuse: Optional[bool] = Field(default=True, description="Enable trading with LLM")

    ## Tracing-Langfuse Configuration
    langfuse_secret_key: Optional[str] = Field(default=None, description="")
    langfuse_public_key: Optional[str] = Field(default=None, description="")
    langfuse_host: Optional[str] = Field(default=None, description="")

    

    @model_validator(mode="before")
    @classmethod
    def validate_api_key(cls, values: Any):
        # If the value is not, get value from environment variable with uppercase key
        for field_name in cls.model_fields:
            field_value = os.getenv(field_name.upper())
            if values.get(field_name) is None or field_value:
                values[field_name] = field_value
        return values

    @classmethod
    def from_json(cls, json_path: str) -> "Config":
        """Load configuration from a JSON file."""
        with open(json_path, "r") as f:
            return cls(**json.load(f))
