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

# Check if Poppler is installed (required for pdf2image)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v pdfinfo &> /dev/null; then
        echo "❌ Poppler is not installed. Installing via Homebrew..."
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
mkdir -p src/pdf_to_markdown_autogen/agents
mkdir -p src/pdf_to_markdown_autogen/utils
mkdir -p output/images
mkdir -p output/markdown
mkdir -p output/logs
touch output/images/.gitkeep
touch output/markdown/.gitkeep
touch output/logs/.gitkeep

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

# Create .env file for OpenAI API key
echo "🔑 Creating .env file for OpenAI API key..."
cat > .env << EOL
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# AutoGen Configuration
AUTOGEN_MODEL=gpt-4-turbo-preview
AUTOGEN_TEMPERATURE=0.7
AUTOGEN_MAX_TOKENS=4096

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
touch src/pdf_to_markdown_autogen/agents/__init__.py
touch src/pdf_to_markdown_autogen/utils/__init__.py

# Create agent files
echo "🤖 Creating AutoGen agent files..."
cat > src/pdf_to_markdown_autogen/agents/pdf_extractor.py << EOL
from typing import Dict, Any
import autogen

class PDFExtractorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are a PDF extraction specialist. Your role is to:
            1. Analyze PDF structure and content
            2. Extract text while preserving formatting
            3. Handle image extraction and placement
            4. Generate initial markdown""",
            llm_config=config
        )
EOL

cat > src/pdf_to_markdown_autogen/agents/md_validator.py << EOL
from typing import Dict, Any
import autogen

class MDValidatorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are a Markdown validation specialist. Your role is to:
            1. Validate generated markdown against the source PDF
            2. Check structure accuracy
            3. Verify content completeness
            4. Ensure proper formatting
            5. Report any issues""",
            llm_config=config
        )
EOL

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
   python -m src.pdf_to_markdown_original.run --input your_pdf_file.pdf --output output/markdown/result.md
4. Run the AutoGen implementation:
   python -m src.pdf_to_markdown_autogen.run_autogen --input your_pdf_file.pdf --output output/markdown/result.md

Project Structure:
├── src/
│   ├── pdf_to_markdown_original/    # Original implementation
│   └── pdf_to_markdown_autogen/     # AutoGen implementation
│       ├── agents/                  # AutoGen agents
│       │   ├── pdf_extractor.py     # PDF extraction agent
│       │   └── md_validator.py      # Markdown validation agent
│       └── utils/                   # Utility functions
├── output/
│   ├── images/                      # Temporary image files
│   ├── markdown/                    # Generated markdown files
│   └── logs/                        # Agent interaction logs
├── venv/                           # Python virtual environment
├── requirements.txt                # Project dependencies
└── .env                           # Environment variables (API keys)

AutoGen Agents:
1. PDFExtractorAgent
   - Analyzes PDF structure and content
   - Extracts text while preserving formatting
   - Handles image extraction and placement
   - Generates initial markdown

2. MDValidatorAgent
   - Validates generated markdown against the source PDF
   - Checks structure accuracy
   - Verifies content completeness
   - Ensures proper formatting
   - Reports any issues
"