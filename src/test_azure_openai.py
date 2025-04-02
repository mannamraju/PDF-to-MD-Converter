#!/usr/bin/env python3
"""Test OpenAI/Azure OpenAI connectivity before running the main application."""

import os
import sys
import logging
from openai import OpenAI, AzureOpenAI
from pdf_to_markdown_autogen.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_api_connection():
    """Test API connectivity with a simple completion request."""
    try:
        # Get configuration
        config = get_config()
        provider_config = config["config_list"][0]
        api_provider = os.getenv("API_PROVIDER", "azure").lower()
        
        logger.info(f"Initializing {api_provider.upper()} client with configuration:")
        logger.info(f"  Model: {provider_config['model']}")
        
        if api_provider == "azure":
            logger.info(f"  Endpoint: {provider_config['base_url']}")
            logger.info(f"  API Version: {provider_config['api_version']}")
            client = AzureOpenAI(
                api_version=provider_config["api_version"],
                azure_endpoint=provider_config["base_url"],
                api_key=provider_config["api_key"]
            )
        else:
            logger.info(f"  Base URL: {provider_config['base_url']}")
            client = OpenAI(
                api_key=provider_config["api_key"],
                base_url=provider_config["base_url"]
            )
        
        # Test completion
        logger.info("Testing API with a simple completion request...")
        response = client.chat.completions.create(
            model=provider_config["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello and confirm you're working!"}
            ],
            max_tokens=100
        )
        
        if response.choices:
            logger.info("Test successful! Response received:")
            logger.info(response.choices[0].message.content)
            return True
        else:
            logger.error("No response choices received")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)