# PDF to Markdown Converter - AutoGen Implementation Documentation

## Architecture Overview

### 1. Core Components

#### Agent System
The implementation uses a sophisticated multi-agent system powered by AutoGen:

1. `PDFExtractorAgent`
   - Analyzes PDF structure and content
   - Preserves text formatting
   - Handles image extraction/placement
   - Generates initial markdown
   - Uses chunked processing for large documents

2. `MDValidatorAgent`
   - Validates generated markdown against source PDF
   - Checks structure accuracy
   - Ensures content completeness
   - Reports formatting issues
   - Performs quality validation

3. `AIProcessor`
   - Coordinates agent interactions
   - Manages rate limiting
   - Handles error recovery
   - Controls processing flow

### 2. Dependencies

#### Core Libraries
- `pyautogen`: Agent framework and coordination
- `openai`: Azure OpenAI API integration
- `PyPDF2`: PDF text extraction
- `pdf2image`: PDF image extraction
- `Pillow`: Image processing
- `opencv-python`: Image analysis
- `numpy`: Numerical operations
- `python-dotenv`: Environment configuration

#### Infrastructure
- Python 3.8+
- Azure OpenAI API access
- Poppler for PDF processing

### 3. Processing Pipeline

1. **Initialization**
   - Load configuration
   - Setup Azure OpenAI connection
   - Initialize rate limiting
   - Create agent instances

2. **Content Extraction**
   - Read PDF file
   - Extract text content
   - Process images
   - Preserve formatting

3. **Content Processing**
   - Chunk text into processable segments
   - Process each chunk with AI
   - Handle rate limits
   - Combine processed chunks

4. **Validation**
   - Compare with source
   - Verify formatting
   - Check completeness
   - Report issues

5. **Output Generation**
   - Format final markdown
   - Include images
   - Save to file

### 4. Error Handling

1. **Rate Limiting**
   - Dynamic intervals
   - Exponential backoff
   - Jitter for retries
   - Consecutive failure tracking

2. **Error Recovery**
   - Graceful degradation
   - Retry mechanisms
   - Detailed logging
   - User feedback

### 5. Configuration

#### Azure OpenAI Settings
```ini
API_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_API_BASE=your-endpoint-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

#### Default Parameters
- Model: o1
- Max Tokens: 40000
- Temperature: Auto-adjusted based on task

### 6. Usage Instructions

1. **Setup**
   ```bash
   cd src/pdf_to_markdown_autogen
   ./init_autogen.sh
   ```

2. **Configuration**
   - Create/edit .env file
   - Set API provider
   - Configure API keys

3. **Running**
   ```bash
   python run_autogen.py
   ```

4. **Output**
   - Markdown files in output/
   - Images in output/images/
   - Logs in conversion.log

### 7. Best Practices

1. **PDF Processing**
   - Pre-validate PDF files
   - Handle large files in chunks
   - Preserve document structure

2. **Rate Management**
   - Monitor API usage
   - Implement backoff strategies
   - Handle rate limits gracefully

3. **Validation**
   - Compare with source
   - Check formatting accuracy
   - Verify image placement

### 8. Troubleshooting

1. **API Issues**
   - Verify credentials
   - Check endpoint configuration
   - Monitor rate limits

2. **Processing Errors**
   - Check PDF compatibility
   - Verify Poppler installation
   - Review chunk sizes

3. **Output Issues**
   - Validate markdown syntax
   - Check image references
   - Verify formatting

### 9. Development Guidelines

1. **Code Structure**
   - Follow modular design
   - Implement proper error handling
   - Maintain clear documentation

2. **Testing**
   - Unit test agents
   - Integration test pipeline
   - Validate output quality

3. **Maintenance**
   - Update dependencies
   - Monitor API changes
   - Review rate limits

### 10. Project Roadmap

#### Current Version (2.0.0)
- Multi-agent system
- Azure OpenAI integration
- Sophisticated rate limiting
- Image extraction and handling

#### Future Enhancements
- Additional language models
- Enhanced formatting options
- Improved error recovery
- Extended validation features