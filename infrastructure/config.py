"""
Configuration management for the application.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    model_type: str = Field(default="OPENAI", description="The type of model to use (OPENAI, VERTEX, LLAMA, AZUREOPENAI)")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    base_model_name: str = Field(default="gpt-3.5-turbo", description="Base model name to use")
    model_path: Optional[str] = Field(default=None, description="Path to LlamaCpp model")
    credentials: Optional[str] = Field(default=None, description="Path to Vertex AI credentials file")
    system_message: Optional[str] = Field(default=None, description="System message to use in chat prompts")
    
    # Azure OpenAI Configuration
    azure_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API Key")
    azure_api_version: str = Field(default="2023-05-15", description="Azure OpenAI API Version")
    azure_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI Endpoint URL")
    azure_deployment_name: Optional[str] = Field(default=None, description="Azure OpenAI Deployment Name")
    azure_embedding_deployment_name: Optional[str] = Field(default=None, description="Azure OpenAI Embedding Deployment Name")
    
    # MongoDB Configuration
    mongo_uri: str = Field(default="mongodb://localhost:27017/chatbot", description="MongoDB connection string")
    mongo_username: Optional[str] = Field(default=None, description="MongoDB username")
    mongo_password: Optional[str] = Field(default=None, description="MongoDB password")
    mongo_database: str = Field(default="langchain_bot", description="MongoDB database name")
    mongo_collection: str = Field(default="chatbot", description="MongoDB collection name")
    mongo_cluster: Optional[str] = Field(default=None, description="MongoDB cluster")
    
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