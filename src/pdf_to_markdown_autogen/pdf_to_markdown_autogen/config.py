import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
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
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        else:  # azure
            self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
            self.api_base = os.getenv('AZURE_OPENAI_API_BASE')
            self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
            if not self.api_key or not self.api_base:
                raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_BASE are required when using Azure OpenAI")
    
    def get_config(self):
        """Get the configuration dictionary for the selected provider."""
        if self.provider == 'openai':
            return {
                'api_key': self.api_key,
                'api_base': self.api_base,
            }
        else:  # azure
            return {
                'api_key': self.api_key,
                'api_base': self.api_base,
                'api_version': self.api_version,
            }
    
    @property
    def is_azure(self):
        """Check if using Azure OpenAI."""
        return self.provider == 'azure'

# Create a global instance
api_config = APIConfig() 