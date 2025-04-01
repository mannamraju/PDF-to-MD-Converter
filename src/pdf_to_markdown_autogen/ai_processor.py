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
        self.consecutive_rate_limits = 0
        
        # Initialize agents
        self.extractor = PDFExtractorAgent(self.config)
        self.validator = MDValidatorAgent(self.config)
    
    def _handle_rate_limit(self, error: Exception) -> None:
        """Handle rate limit errors and track consecutive occurrences."""
        if "429" in str(error):
            self.consecutive_rate_limits += 1
            logger.warning(f"Rate limit hit. Consecutive occurrences: {self.consecutive_rate_limits}")
            
            if self.consecutive_rate_limits >= 3:
                logger.error("Quitting after 3 consecutive rate limit errors")
                raise Exception("Rate limit exceeded 3 times consecutively. Please try again later.")
            
            # Reset counter if we get a successful response
            self.consecutive_rate_limits = 0
        raise error
    
    def process(self) -> Optional[Path]:
        """Process the PDF and generate markdown output."""
        try:
            logger.info(f"Starting PDF processing: {self.pdf_path}")
            
            # Extract content from PDF
            logger.info("Extracting content from PDF...")
            try:
                markdown_content = self.extractor.extract_content(str(self.pdf_path))
            except Exception as e:
                self._handle_rate_limit(e)
            
            # Get original text for validation
            original_text = self.extractor.extract_text(str(self.pdf_path))
            
            # Validate the generated markdown
            logger.info("Validating generated markdown...")
            try:
                validation_result = self.validator.validate_markdown(markdown_content, original_text)
                logger.info("Validation successful")
            except Exception as e:
                self._handle_rate_limit(e)
            
            # Save the markdown content
            output_file = self.pdf_path.parent / "output" / f"{self.pdf_path.stem}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Successfully processed PDF. Output saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return None 