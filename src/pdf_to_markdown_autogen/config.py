"""Configuration module for PDF to Markdown converter."""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class APIConfig:
    """Configuration class for Azure OpenAI settings."""
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        self.model = os.getenv('AUTOGEN_MODEL', 'o1')
        self.deployment = os.getenv('AUTOGEN_MODEL', 'o1')
    
    def validate(self):
        """Validate the Azure OpenAI configuration."""
        if not self.api_key or not self.azure_endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required")
    
    def get_config(self):
        """Get the Azure OpenAI configuration dictionary."""
        self.validate()
        
        # Base config for autogen
        config = {
            "config_list": [{
                "model": self.model,
                "api_key": self.api_key,
                "base_url": self.azure_endpoint,
                "api_type": "azure",
                "api_version": self.api_version
            }],
            "temperature": float(os.getenv('AUTOGEN_TEMPERATURE', '1.0')),
            "max_tokens": int(os.getenv('AUTOGEN_MAX_TOKENS', '40000'))
        }
        
        return config

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables using APIConfig."""
    return api_config.get_config()

def get_azure_config() -> Dict[str, Any]:
    """Get Azure OpenAI configuration from environment variables."""
    return {
        "config_list": [{
            "model": os.getenv("AZURE_OPENAI_MODEL", "o1"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY", "C8W0q3rogNmf0fbaTbl360ZUbq4jfQ8cCii8b0qq6EAOaLpb5BrXJQQJ99ALACYeBjFXJ3w3AAABACOGyYI9"),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "https://maopenai050.openai.azure.com/"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        }],
        "max_tokens": int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "40000"))
    }

# Create a global instance
api_config = APIConfig() 