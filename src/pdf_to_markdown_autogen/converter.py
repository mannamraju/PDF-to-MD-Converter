import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent
from .version import __version__

logger = logging.getLogger(__name__)

class PDFToMarkdownConverter:
    """Main class for converting PDFs to Markdown."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the converter with configuration."""
        # Load environment variables if not provided
        if config is None:
            load_dotenv()
            from .config import api_config
            config = api_config.get_config()
        
        self.config = config
        self.pdf_extractor = PDFExtractorAgent(config)
        self.md_validator = MDValidatorAgent(config)
        
        logger.info(f"Initializing PDF to Markdown Converter v{__version__}")
    
    def convert(self, pdf_path: str) -> str:
        """Convert a PDF file to Markdown format."""
        logger.info(f"Starting PDF to Markdown conversion v{__version__}")
        
        # Extract content from PDF
        markdown_content = self.pdf_extractor.extract_content(pdf_path)
        
        # Validate markdown content
        # For validation, we'll use a sample of the original text
        # This is more efficient than validating the entire document
        with open(pdf_path, 'rb') as file:
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            sample_text = ""
            for i in range(min(2, len(reader.pages))):
                sample_text += reader.pages[i].extract_text()
        
        # Only validate if we have enough text
        if len(sample_text) > 100:
            is_valid = self.md_validator.validate_markdown(markdown_content, sample_text)
            if not is_valid:
                logger.warning("Markdown validation failed, but continuing with output")
        
        return markdown_content

def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), None)
    
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Disable verbose logging from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("autogen").setLevel(logging.WARNING)
    
    # Only log essential messages from our application
    logging.getLogger("pdf_to_markdown_autogen").setLevel(logging.INFO)
    
    logger.info(f"Logging configured with level: {log_level}") 