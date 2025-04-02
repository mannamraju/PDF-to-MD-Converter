#!/bin/bash

# Exit on error
set -e

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Initializing PDF to Markdown Converter (Original Implementation)..."

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

# Install development dependencies
echo "🔧 Installing development dependencies..."
rye sync --dev

# Make the script executable
chmod +x "$SCRIPT_DIR/init_original.sh"

echo "✨ Original implementation initialization complete!"
echo "
Next steps:
1. Run the original implementation:
   rye run python -m src.pdf_to_markdown_original.run
" 