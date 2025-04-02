#!/bin/bash

# Set script to exit on error
set -e

echo "Running Azure OpenAI connection test..."

# Make the test file executable if it's not already
chmod +x src/test_azure_openai.py

# Run the test script
python3 src/test_azure_openai.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Azure OpenAI connection test successful!"
else
    echo "❌ Azure OpenAI connection test failed!"
    exit 1
fi

echo "You can now proceed with running the main application."
