import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class APIConfig:
    """Configuration class for API settings."""
    
    def __init__(self):
        self.provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        if self.provider not in ['openai', 'azure']:
            raise ValueError("API_PROVIDER must be either 'openai' or 'azure'")
        
        if self.provider == 'openai':
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        else:  # azure
            self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
            self.api_base = os.getenv('AZURE_OPENAI_API_BASE')
            self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    
    def validate(self):
        """Validate the configuration based on the selected provider."""
        if self.provider == 'openai' and not self.api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        elif self.provider == 'azure' and (not self.api_key or not self.api_base):
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_BASE are required when using Azure OpenAI")
    
    def get_config(self):
        """Get the configuration dictionary for the selected provider."""
        self.validate()  # Validate before returning config
        
        # Base config for both providers
        config = {
            'temperature': float(os.getenv('AUTOGEN_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('AUTOGEN_MAX_TOKENS', '4096')),
        }
        
        # Add provider-specific config
        if self.provider == 'openai':
            config.update({
                'model': os.getenv('AUTOGEN_MODEL', 'gpt-4-turbo-preview'),
                'api_key': self.api_key,
                'base_url': self.api_base,
            })
        else:  # azure
            config.update({
                'model': os.getenv('AUTOGEN_MODEL', 'gpt-4o'),
                'api_key': self.api_key,
                'base_url': self.api_base,
                'api_version': self.api_version,
                'api_type': 'azure',
            })
        
        return config
    
    @property
    def is_azure(self):
        """Check if using Azure OpenAI."""
        return self.provider == 'azure'

# Create a global instance
api_config = APIConfig() 