#!/bin/bash

# Exit on error
set -e

echo "🚀 Initializing PDF to Markdown Converter project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 before continuing."
    exit 1
else
    echo "✅ Python 3 is installed"
fi

# Check if Poppler is installed
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v pdfinfo &> /dev/null; then
        echo "❌ Poppler is not installed. Installing via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install poppler
        echo "✅ Poppler installed successfully"
    else
        echo "✅ Poppler is already installed"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if ! command -v pdfinfo &> /dev/null; then
        echo "❌ Poppler is not installed. Installing via apt..."
        sudo apt-get update
        sudo apt-get install -y poppler-utils
        echo "✅ Poppler installed successfully"
    else
        echo "✅ Poppler is already installed"
    fi
else
    echo "⚠️  Windows detected. Please install Poppler manually if not already installed:"
    echo "1. Download from: http://blog.alivate.com.au/poppler-windows/"
    echo "2. Extract to a directory (e.g., C:\Program Files\poppler)"
    echo "3. Add the bin directory to your system PATH"
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p src/pdf_to_markdown_original
mkdir -p src/pdf_to_markdown_autogen
mkdir -p output/images
touch output/images/.gitkeep

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment based on OS
if [[ "$OSTYPE" == "win"* ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install -r requirements-dev.txt

# Create .env file for OpenAI API key
echo "🔑 Creating .env file for OpenAI API key..."
cat > .env << EOL
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Uncomment for Azure OpenAI
# API_PROVIDER=azure
# AZURE_OPENAI_API_KEY=your-azure-key-here
# AZURE_OPENAI_API_BASE=https://your-service-name.openai.azure.com/openai/deployments/your-deployment-name
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
EOL

# Create __init__.py files for Python modules
touch src/__init__.py
touch src/pdf_to_markdown_original/__init__.py
touch src/pdf_to_markdown_autogen/__init__.py

# Make the script executable
if [[ "$OSTYPE" != "win"* ]]; then
    chmod +x init_project.sh
fi

echo "✨ Project initialization complete!"
echo "
Next steps:
1. Edit .env file and add your OpenAI API key
2. Activate the virtual environment:
   - On Windows: .\\venv\\Scripts\\activate
   - On macOS/Linux: source venv/bin/activate
3. Run the original implementation:
   python -m src.pdf_to_markdown_original.run --input your_pdf_file.pdf --output output/result.md
4. Run the AutoGen implementation:
   python -m src.pdf_to_markdown_autogen.run --input your_pdf_file.pdf --output output/result.md
"