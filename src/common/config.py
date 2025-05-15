"""
Configuration management for the application.
"""

import os
from typing import Optional, Any

from pydantic_settings import SettingsConfigDict
from pydantic import Field, model_validator, BaseModel


class EnvironmentVariable(BaseModel):
    # Azure OpenAI Configuration
    azure_chat_model_key: Optional[str] = Field(default=None, description="Azure OpenAI API Key")
    azure_chat_model_version: Optional[str] = Field(default=None, description="Azure OpenAI API Version")
    azure_chat_model_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI Endpoint URL")
    azure_chat_model_deployment: Optional[str] = Field(default=None, description="Azure OpenAI Deployment Name")

    # MongoDB Configuration
    mongo_uri: Optional[str] = Field(default=None, description="MongoDB connection string")
    mongo_username: Optional[str] = Field(default=None, description="MongoDB username")
    mongo_password: Optional[str] = Field(default=None, description="MongoDB password")
    mongo_database: Optional[str] = Field(default=None, description="MongoDB database name")
    mongo_collection: Optional[str] = Field(default=None, description="MongoDB collection name")
    mongo_cluster: Optional[str] = Field(default=None, description="MongoDB cluster")

    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    base_model_name: Optional[str] = Field(default=None, description="Base model name to use")
    model_path: Optional[str] = Field(default=None, description="Path to LlamaCpp model")
    credentials: Optional[str] = Field(default=None, description="Path to Vertex AI credentials file")
    system_message: Optional[str] = Field(default=None, description="System message to use in chat prompts")

    @model_validator(mode="before")
    @classmethod
    def validate_api_key(cls, values: Any):
        # If the value is not, get value from environment variable with uppercase key
        for field_name in cls.model_fields:
            if values.get(field_name) is None:
                field_value = os.getenv(field_name.upper())
                values[field_name] = field_value
        return values


class Config(BaseModel):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    model_type: str = Field(default="OPENAI", description="The type of model to use (OPENAI, VERTEX, LLAMA, AZUREOPENAI)")
    # Memory Configuration
    memory_type: str = Field(default="custom", description="Type of memory to use (custom, mongo)")
    memory_window_size: int = Field(default=5, description="Number of messages to include in the context window")
    
    # Server Configuration
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Bot Configuration
    ai_prefix: str = Field(default="AI", description="Prefix for AI messages in the prompt")
    human_prefix: str = Field(default="Human", description="Prefix for human messages in the prompt")
    memory_key: str = Field(default="history", description="Key to use for conversation history")
    
    # Miscellaneous
    enable_anonymizer: bool = Field(default=False, description="Enable PII anonymization")
    serp_api_token: Optional[str] = Field(default=None, description="SERP API token for web search")
    
    # Environment settings
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    env_vars: EnvironmentVariable = EnvironmentVariable()
