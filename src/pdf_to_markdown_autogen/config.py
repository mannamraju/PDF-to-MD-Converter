"""Configuration module for PDF to Markdown converter."""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class APIConfig:
    """Configuration class for API settings."""
    
    def __init__(self):
        # Get API provider from environment, default to OpenAI
        self.api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        self.is_azure = self.api_provider == 'azure'
        
        # Common settings
        self.temperature = float(os.getenv('AUTOGEN_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('AUTOGEN_MAX_TOKENS', '40000'))
        
        if self.is_azure:
            # Azure OpenAI settings
            self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
            self.base_url = os.getenv('AZURE_OPENAI_ENDPOINT')
            self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
            self.model = os.getenv('AZURE_OPENAI_MODEL', 'o1')
        else:
            # OpenAI settings
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    
    def validate(self):
        """Validate the API configuration."""
        if not self.api_key:
            key_var = 'AZURE_OPENAI_API_KEY' if self.is_azure else 'OPENAI_API_KEY'
            raise ValueError(f"{key_var} is required")
        
        if self.is_azure and not self.base_url:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI")
    
    def get_config(self):
        """Get the API configuration dictionary."""
        self.validate()
        
        # Base config for autogen
        config = {
            "config_list": [{
                "model": self.model,
                "api_key": self.api_key,
                "base_url": self.base_url,
            }],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # Add Azure-specific settings if using Azure
        if self.is_azure:
            config["config_list"][0].update({
                "api_type": "azure",
                "api_version": self.api_version
            })
        
        return config

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables using APIConfig."""
    return api_config.get_config()

# Create a global instance
api_config = APIConfig()