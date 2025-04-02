#!/usr/bin/env python3
"""Test Azure OpenAI connectivity before running the main application."""

import os
import sys
import logging
from openai import AzureOpenAI
from pdf_to_markdown_autogen.config import get_azure_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_azure_openai_connection():
    """Test Azure OpenAI connectivity with a simple completion request."""
    try:
        # Get configuration
        config = get_azure_config()
        azure_config = config["config_list"][0]
        
        logger.info("Initializing Azure OpenAI client with configuration:")
        logger.info(f"  Model: {azure_config['model']}")
        logger.info(f"  Endpoint: {azure_config['azure_endpoint']}")
        logger.info(f"  API Version: {azure_config['api_version']}")
        
        # Initialize client
        client = AzureOpenAI(
            api_version=azure_config["api_version"],
            azure_endpoint=azure_config["azure_endpoint"],
            api_key=azure_config["api_key"]
        )
        
        # Test completion
        logger.info("Testing API with a simple completion request...")
        response = client.chat.completions.create(
            model=azure_config["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello and confirm you're working!"}
            ],
            max_completion_tokens=100
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
    success = test_azure_openai_connection()
    sys.exit(0 if success else 1) 