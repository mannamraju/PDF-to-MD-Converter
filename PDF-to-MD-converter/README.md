# PDF to Markdown Converter

## Overview
This project is a PDF to Markdown converter that allows users to convert PDF documents into Markdown format. It includes both an original implementation and an auto-generated version.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PDF-to-MD-converter.git
   cd PDF-to-MD-converter
   ```

2. **Run the initialization script:**
   ```bash
   bash init_project.sh
   ```

3. **Edit the `.env` file:**
   Add your OpenAI API key and other necessary configurations.

4. **Install dependencies:**
   ```bash
   rye sync
   ```

## Dependencies
- `rye`: Dependency management tool
- `poppler-utils`: Required for PDF processing

## Running the Project
To run the original implementation:
```bash
rye run python -m src.pdf_to_markdown_original.run
```

To run the AutoGen implementation:
```bash
rye run python -m src.pdf_to_markdown_autogen.run
```

## Testing
To run the tests, use:
```bash
pytest tests
```

## License
This project is licensed under the MIT License.