# PDF to Markdown Converter (Original Implementation)

A Python tool that converts PDF documents to Markdown format while making the best attempt at preserving text formatting, tables, and images. This is the original implementation that works completely offline.

## Features

- Makes best attempt to convert PDF text to well-formatted Markdown
- Preserves document structure (headings, lists, tables)
- Extracts and embeds images from PDF
- Handles various image formats (JPEG, PNG, JPEG2000, TIFF)
- Makes best attempt to preserve image quality and transparency
- Sanitizes sensitive information (emails, company names)
- Generates detailed conversion logs
- Works completely offline - no internet connection required

## Prerequisites

- Python 3.8 or higher
- Rye (Python package manager)
- Poppler (for PDF processing)

### Installing Prerequisites

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Poppler
brew install poppler
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

#### Windows
1. Download Poppler from: http://blog.alivate.com.au/poppler-windows/
2. Extract to a directory (e.g., `C:\Program Files\poppler`)
3. Add the bin directory to your system PATH

## Installation

1. Navigate to the original implementation directory:
```bash
cd src/pdf_to_markdown_original
```

2. Run the initialization script:
```bash
./init_original.sh
```

This will:
- Check and install Rye if needed
- Check and install Poppler if needed
- Create necessary directories
- Install Python dependencies
- Install development dependencies

## Usage

1. Make sure you're in the original implementation directory:
```bash
cd src/pdf_to_markdown_original
```

2. Run the converter:
```bash
rye run python run.py
```

3. Follow the prompts to:
   - Enter the path to your PDF file
   - Specify an output directory (optional, defaults to "output")

## Output Structure

```
output/
├── images/              # Extracted images
│   ├── image_1_1.png
│   ├── image_1_2.png
│   └── ...
├── your_document.md     # Generated markdown file
└── conversion.log       # Detailed conversion log
```

## Development

### Setting up Development Environment

1. Make sure you're in the original implementation directory:
```bash
cd src/pdf_to_markdown_original
```

2. Install development dependencies:
```bash
rye sync --dev
```

3. Activate the virtual environment:
```bash
.venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate  # On Windows
```

### Running Tests

```bash
rye run pytest
```

## Version History

### v1.1.0
- Added improved image extraction with white background preservation

### v1.0.0
- Initial release with basic PDF to Markdown conversion

## Note

This is the original implementation. For the newer AutoGen-based implementation with AI agents, see the `pdf_to_markdown_autogen` directory. 