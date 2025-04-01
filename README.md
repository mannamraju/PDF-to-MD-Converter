# PDF to Markdown Converter

A powerful tool that converts PDF documents to well-formatted Markdown, preserving structure, formatting, and images.

## Features

- Structure preservation and formatting
- Intelligent image extraction and placement
- Support for tables and complex layouts
- Two implementations:
  - Original: Offline implementation using Python libraries
  - AutoGen: AI-powered implementation using AutoGen agents

## Prerequisites

- Python 3.8 or higher
- Poppler for PDF processing (required for image extraction)

### Installing Poppler

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

**Windows:**
1. Download from: http://blog.alivate.com.au/poppler-windows/
2. Extract to a directory (e.g., C:\Program Files\poppler)
3. Add the bin directory to your system PATH

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PDF-to-MD-converter.git
cd PDF-to-MD-converter
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. For development, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Configure your API settings (for AutoGen implementation):
   Create a `.env` file in the project root:

   ```
   # OpenAI API Configuration
   OPENAI_API_KEY=your-api-key-here
   OPENAI_API_BASE=https://api.openai.com/v1
   
   # Uncomment for Azure OpenAI
   # API_PROVIDER=azure
   # AZURE_OPENAI_API_KEY=your-azure-key-here
   # AZURE_OPENAI_API_BASE=https://your-service-name.openai.azure.com/openai/deployments/your-deployment-name
   # AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## Usage

### Original Implementation

```bash
python -m src.pdf_to_markdown_original.run --input your_pdf_file.pdf --output output/result.md
```

### AutoGen Implementation

```bash
python -m src.pdf_to_markdown_autogen.run --input your_pdf_file.pdf --output output/result.md
```

## Output Structure

```
output/
├── images/           # Extracted images from PDFs
├── *.md              # Generated markdown files
└── conversion.log    # Detailed conversion logs
```

## Implementation Details

### Original Implementation
The original implementation uses Python libraries such as PDFMiner and PyMuPDF to extract text and images from PDF files, preserving the structure and formatting as much as possible.

### AutoGen Implementation
The AI-powered implementation uses AutoGen agents for enhanced processing:

1. **PDFExtractorAgent**
   - Analyzes PDF structure and content
   - Extracts text while preserving formatting
   - Handles image extraction and placement
   - Generates initial markdown

2. **MDValidatorAgent**
   - Validates generated markdown against the source PDF
   - Checks structure accuracy
   - Verifies content completeness
   - Ensures proper formatting
   - Reports any issues

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src tests
isort src tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.