import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

try:
    from dotenv import load_dotenv
    from pdf_to_markdown_autogen.agents.pdf_extractor import PDFExtractorAgent
    from pdf_to_markdown_autogen.agents.md_validator import MDValidatorAgent
    from pdf_to_markdown_autogen.config import api_config, get_azure_config

    # Load environment variables
    load_dotenv()
    logger.debug("Environment variables loaded")

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
        
        # Get original text for validation
        logger.info("Getting original text for validation...")
        original_text = pdf_extractor.get_text_content(input_file)
        
        # Validate markdown content
        logger.info("Validating markdown content...")
        is_valid, validation_result = md_validator.validate_markdown(markdown_content, original_text)
        
        if not is_valid:
            logger.warning(f"Validation issues found: {validation_result}")
        
        # Save markdown content
        logger.info(f"Saving markdown content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info("Conversion completed successfully")

    def main():
        # Get the current directory
        current_dir = Path(__file__).parent
        
        # Set paths
        pdf_path = current_dir.parent / "DIGITAL-Spike_ Evaluate Spark Engine in Azure Fabric-270325-192159.pdf"
        output_dir = current_dir.parent / "output"
        
        # Extract full paths
        input_file = str(pdf_path.resolve())
        output_file = str((output_dir / pdf_path.stem).resolve().with_suffix('.md'))
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF to markdown
        convert_pdf_to_markdown(input_file, output_file)

    if __name__ == "__main__":
        try:
            main()
        except Exception as e:
            logger.error(f"Error in main execution: {str(e)}", exc_info=True)
            sys.exit(1)

except Exception as e:
    logger.error(f"Error during initialization: {str(e)}", exc_info=True)
    sys.exit(1)