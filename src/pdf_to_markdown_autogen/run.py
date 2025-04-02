import os
import sys
import logging
from pathlib import Path
from .agents.pdf_extractor import PDFExtractorAgent
from .agents.md_validator import MDValidatorAgent
from .config import get_azure_config

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from pdf_to_markdown_autogen.run_autogen import main

logger = logging.getLogger(__name__)

def convert_pdf_to_markdown(input_file: str, output_file: str) -> None:
    """
    Convert a PDF file to Markdown using the AutoGen implementation.
    
    Args:
        input_file (str): Path to the input PDF file
        output_file (str): Path where the output Markdown file should be saved
    """
    # Get configuration
    config = get_azure_config()
    
    # Initialize agents
    pdf_extractor = PDFExtractorAgent(config)
    md_validator = MDValidatorAgent(config)
    
    # Extract content from PDF
    logger.info("Extracting content from PDF...")
    markdown_content = pdf_extractor.extract_content(input_file)
    
    # Validate markdown content
    logger.info("Validating markdown content...")
    is_valid, validation_result = md_validator.validate_content(markdown_content, input_file)
    
    if not is_valid:
        logger.warning(f"Validation issues found: {validation_result}")
    
    # Save markdown content
    logger.info(f"Saving markdown content to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    logger.info("Conversion completed successfully")

if __name__ == "__main__":
    main() 