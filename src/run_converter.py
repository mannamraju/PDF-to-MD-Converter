#!/usr/bin/env python3
"""
PDF to Markdown Converter - Main Script
"""

import os
import sys
import logging
from pathlib import Path
from pdf_to_markdown_autogen.ai_processor import AIProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Hardcoded input file path
    input_file = "/Users/mannamraju/localCode/DMAIO-ST-One-Data-Feed-Kubernetes-Edge-270325-191539.pdf"
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Starting conversion of {input_file}")
    try:
        # Use AutoGen processor
        processor = AIProcessor(input_file)
        output_file = processor.process()
        
        if output_file is None:
            logger.error("Conversion failed - see above errors for details")
            sys.exit(1)
        
        logger.info(f"Conversion completed successfully. Output saved to {output_file}")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()