from pathlib import Path
import logging
from typing import Optional
from .config import api_config
from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIProcessor:
    """Coordinates the AI agents for PDF processing."""
    
    def __init__(self, pdf_path: str):
        """Initialize the processor with the PDF path."""
        self.pdf_path = Path(pdf_path)
        self.config = api_config.get_config()
        
        # Initialize agents
        self.extractor = PDFExtractorAgent(self.config)
        self.validator = MDValidatorAgent(self.config)
    
    def process(self) -> Optional[Path]:
        """Process the PDF and generate markdown output."""
        try:
            logger.info(f"Starting PDF processing: {self.pdf_path}")
            
            # Extract content from PDF
            logger.info("Extracting content from PDF...")
            markdown_content = self.extractor.extract_content(str(self.pdf_path))
            
            # Get original text for validation
            original_text = self.extractor.extract_text(str(self.pdf_path))
            
            # Validate the generated markdown
            logger.info("Validating generated markdown...")
            validation_result = self.validator.validate_markdown(markdown_content, original_text)
            
            # Log validation results
            if "Critical Issues Found:" in validation_result:
                logger.warning("Validation found issues:\n%s", validation_result)
            else:
                logger.info("Validation successful")
            
            # Save the markdown content
            output_file = self.pdf_path.parent / "output" / f"{self.pdf_path.stem}.md"
            output_file.write_text(markdown_content)
            logger.info(f"Successfully processed PDF. Output saved to: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return None 