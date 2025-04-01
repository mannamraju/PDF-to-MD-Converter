import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from pdf_to_markdown_autogen.run_autogen import main

if __name__ == "__main__":
    main() 