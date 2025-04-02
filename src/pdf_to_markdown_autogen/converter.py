from typing import Dict, Any
import logging
from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent
from .version import __version__

logger = logging.getLogger(__name__)

class PDFToMarkdownConverter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pdf_extractor = PDFExtractorAgent(config)
        self.md_validator = MDValidatorAgent(config)
        logger.info(f"Initializing PDF to Markdown Converter v{__version__}")
    
    def convert(self, pdf_path: str, output_path: str = None) -> str:
        """Convert PDF to Markdown with version tracking."""
        logger.info(f"Starting PDF to Markdown conversion v{__version__}")
        
        # Extract content
        markdown_content = self.pdf_extractor.extract_content(pdf_path)
        
        # Validate content
        validation_result = self.md_validator.validate_markdown(
            markdown_content,
            self.pdf_extractor.extract_text(pdf_path)
        )
        
        # Save output if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"Conversion completed successfully. Output saved to {output_path}")
        
        return markdown_content 