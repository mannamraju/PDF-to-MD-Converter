import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

from pdf_to_markdown_autogen.ai_processor import AIProcessor
from pdf_to_markdown_autogen.config import api_config
from dotenv import load_dotenv

if __name__ == "__main__":
    from run import main
    main()