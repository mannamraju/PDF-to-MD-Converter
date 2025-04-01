#!/bin/bash

# Exit on error
set -e

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Initializing PDF to Markdown Converter (AutoGen Implementation)..."

# Check if we're in the correct directory
if [ ! -f "$SCRIPT_DIR/pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found in $SCRIPT_DIR"
    echo "Please make sure you're running this script from the correct directory"
    exit 1
fi

# Check if Rye is installed
if ! command -v rye &> /dev/null; then
    echo "❌ Rye is not installed. Installing Rye..."
    curl -sSf https://rye-up.com/get | bash
    echo "✅ Rye installed successfully"
else
    echo "✅ Rye is already installed"
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
    echo "⚠️  Unsupported operating system. Please install Poppler manually."
    echo "For Windows:"
    echo "1. Download from: http://blog.alivate.com.au/poppler-windows/"
    echo "2. Extract to a directory (e.g., C:\Program Files\poppler)"
    echo "3. Add the bin directory to your system PATH"
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p "$SCRIPT_DIR/../../output/images"

# Change to script directory
cd "$SCRIPT_DIR"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
rye sync

# Create .env file only if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "🔑 Creating .env file for API configuration..."
    cat > "$SCRIPT_DIR/.env" << EOL
# Choose your API provider: "openai" or "azure"
API_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your-openai-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_API_BASE=https://your-service-name.openai.azure.com/openai/deployments/your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
EOL
    echo "✅ Created new .env file"
else
    echo "✅ .env file already exists, skipping creation"
fi

# Make the script executable
chmod +x "$SCRIPT_DIR/init_autogen.sh"

echo "✨ AutoGen implementation initialization complete!"
echo "
Next steps:
1. Edit .env file and configure your API settings:
   - Set API_PROVIDER to 'openai' or 'azure'
   - Add your API key and endpoint
2. Run the AutoGen implementation:
   rye run python run_autogen.py
" 