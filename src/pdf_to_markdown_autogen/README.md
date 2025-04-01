# PDF to Markdown Converter (AutoGen Implementation)

This is the AI-powered implementation of the PDF to Markdown converter that uses AutoGen agents for enhanced processing.

## Features

- AI-powered content analysis and extraction
- Two-agent system for content extraction and validation
- Structure preservation and formatting
- Intelligent image extraction and placement
- Automated validation of generated markdown
- Detailed conversion logs
- Support for both OpenAI and Azure OpenAI APIs

## Prerequisites

- Python 3.8 or higher
- Rye (Python package manager)
- Poppler for PDF processing
- OpenAI API key or Azure OpenAI credentials

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PDF_reader
   ```

2. Run the initialization script:
   ```bash
   cd src/pdf_to_markdown_autogen
   ./init_autogen.sh
   ```

3. Configure your API settings:
   Edit the `.env` file in the `src/pdf_to_markdown_autogen` directory:

   For OpenAI:
   ```
   API_PROVIDER=openai
   OPENAI_API_KEY=your-openai-key-here
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

   For Azure OpenAI:
   ```
   API_PROVIDER=azure
   AZURE_OPENAI_API_KEY=your-azure-key-here
   AZURE_OPENAI_API_BASE=https://your-service-name.openai.azure.com/openai/deployments/your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

## Usage

1. Place your PDF file in the project directory or specify its path when running the converter.

2. Run the converter:
   ```bash
   rye run python run_autogen.py
   ```

3. The converted markdown file will be saved in the `output` directory.

## Agent System

The implementation uses two specialized AutoGen agents:

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

## Output Structure

```
output/
├── images/           # Extracted images from PDFs
├── *.md             # Generated markdown files
└── conversion.log   # Detailed conversion logs
```

## Version History

- v2.0.0: Initial release with AutoGen implementation

## Note

This is the AI-powered implementation. For the original offline implementation, see the `pdf_to_markdown_original` directory. 