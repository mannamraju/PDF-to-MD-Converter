from pathlib import Path
import logging
import re
from typing import Optional
from .config import api_config
from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent
from .version import __version__

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
    
    def _increment_version(self) -> None:
        """Increment the patch version number after successful conversion."""
        version_file = Path(__file__).parent / "version.py"
        try:
            with open(version_file, 'r') as f:
                content = f.read()
            
            # Extract current version
            match = re.search(r'__version__\s*=\s*"(\d+\.\d+\.\d+)"', content)
            if not match:
                logger.warning("Could not find version number to increment")
                return
            
            current_version = match.group(1)
            major, minor, patch = map(int, current_version.split('.'))
            new_version = f"{major}.{minor}.{patch + 1}"
            
            # Update version file
            new_content = content.replace(f'__version__ = "{current_version}"', f'__version__ = "{new_version}"')
            with open(version_file, 'w') as f:
                f.write(new_content)
            
            logger.info(f"Version incremented from {current_version} to {new_version}")
            
        except Exception as e:
            logger.warning(f"Failed to increment version: {str(e)}")
    
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
                error_msg = f"Failed to extract content from PDF: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            if not markdown_content:
                error_msg = "No content was extracted from the PDF"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Get original text for validation
            original_text = "\n\n".join(self.extractor.extract_text(str(self.pdf_path)))
            
            # Validate the generated markdown
            logger.info("Validating generated markdown...")
            try:
                is_valid, validation_details = self.validator.validate_markdown(markdown_content, original_text)
                if not is_valid:
                    error_msg = f"Validation failed: {validation_details}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                logger.info("Validation successful")
            except Exception as e:
                if "429" in str(e):
                    self._handle_rate_limit(e)
                error_msg = f"Error during markdown validation: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Save the markdown content
            output_file = self.pdf_path.parent / "output" / f"{self.pdf_path.stem}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            except Exception as e:
                error_msg = f"Failed to save markdown file: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Increment version number on successful completion
            self._increment_version()
            
            logger.info(f"Successfully processed PDF. Output saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            return None