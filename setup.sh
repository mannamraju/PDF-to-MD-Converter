#!/bin/bash

# Exit on error
set -e

# Source bash profile for proper environment setup
if [ -f ~/.bash_profile ]; then
    source ~/.bash_profile
fi

echo "🚀 Setting up PDF to Markdown Converter..."

# Ensure we're using Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Check Python version (fixed version comparison)
python_version=$(python3 -c 'import sys; print(sys.version_info[0] * 100 + sys.version_info[1])')
if [ "$python_version" -lt 308 ]; then
    echo "❌ Python 3.8 or higher required"
    exit 1
fi
echo "✅ Python version $(python3 --version)"

# Install Poppler based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v pdfinfo &> /dev/null; then
        echo "Installing Poppler via Homebrew..."
        brew install poppler
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! command -v pdfinfo &> /dev/null; then
        echo "Installing Poppler via apt..."
        sudo apt-get update && sudo apt-get install -y poppler-utils
    fi
else
    echo "⚠️ Please install Poppler manually on Windows:"
    echo "1. Download from: http://blog.alivate.com.au/poppler-windows/"
    echo "2. Extract to C:\Program Files\poppler"
    echo "3. Add to PATH: C:\Program Files\poppler\bin"
fi

# Create and activate virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
echo "export PYTHONPATH=\"\${PYTHONPATH}:$(pwd)/src\"" >> .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p output/{images,markdown,logs}

# Create .env from example if it doesn't exist
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "📝 Created .env from template. Please edit with your API keys"
fi

# Make scripts executable
chmod +x setup.sh
find . -name "*.sh" -exec chmod +x {} \;

echo "
✨ Setup complete! Next steps:

1. Edit .env file with your API keys
2. Activate the virtual environment:
   source .venv/bin/activate

3. Run the converter:
   - Original implementation:
     python -m src.pdf_to_markdown_original.run
   
   - AutoGen implementation:
     python -m src.pdf_to_markdown_autogen.run_autogen

Note: The virtual environment setup has added the src directory to PYTHONPATH
"