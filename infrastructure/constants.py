"""
Application-wide constants.

This module contains constants used throughout the application.
"""

# Environment variable keys
OPENAI_API_KEY = "OPENAI_API_KEY"
MONGO_URI = "MONGO_URI"
MONGO_DATABASE = "MONGO_DATABASE"
MONGO_COLLECTION = "MONGO_COLLECTION"
MONGO_USERNAME = "MONGO_USERNAME"
MONGO_PASSWORD = "MONGO_PASSWORD"
MONGO_CLUSTER = "MONGO_CLUSTER"
MODEL_TYPE = "MODEL_TYPE"
CREDENTIALS_FILE = "CREDENTIALS_FILE"
AI_PREFIX = "AI_PREFIX"
HUMAN_PREFIX = "HUMAN_PREFIX"
MEMORY_KEY = "MEMORY_KEY"

# Default values
DEFAULT_PORT = 8000
DEFAULT_HOST = "0.0.0.0"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MEMORY_TYPE = "custom"
DEFAULT_MEMORY_WINDOW_SIZE = 5
DEFAULT_CONVERSATION_ID = "default_conversation"

# Message roles
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_FUNCTION = "function"

# NLP Configuration
NLP_CONFIG = {
    "model": "en_core_web_sm",
    "exclude_ner_types": ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]
}

# Fields to anonymize in PII protection
ANONYMIZED_FIELDS = [
    "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT",
    "WORK_OF_ART", "LAW", "LANGUAGE", "FAC", "NORP"
]

# API Version
API_VERSION = "v1" 