from pathlib import Path
import logging
from typing import List, Dict
from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent
from .config import api_config

class AIProcessor:
    """Coordinates the AI agents for PDF processing."""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / "conversion.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents with API configuration
        config = api_config.get_config()
        self.extractor = PDFExtractorAgent(config)
        self.validator = MDValidatorAgent(config)
    
    def process(self) -> str:
        """Process a PDF file using AI agents."""
        try:
            self.logger.info(f"Starting PDF processing: {self.pdf_path}")
            
            # Extract content
            self.logger.info("Extracting content from PDF...")
            markdown_content = self.extractor.extract_content(str(self.pdf_path))
            
            # Validate markdown
            self.logger.info("Validating generated markdown...")
            is_valid, validation_report = self.validator.validate_markdown(str(self.pdf_path), markdown_content)
            
            if not is_valid:
                self.logger.warning("Markdown validation failed. Check the log for details.")
                self.logger.info(f"Validation report: {validation_report}")
            
            # Save markdown file
            output_file = self.output_dir / f"{self.pdf_path.stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Successfully processed PDF. Output saved to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise 