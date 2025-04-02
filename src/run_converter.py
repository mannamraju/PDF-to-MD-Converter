import os
from dotenv import load_dotenv
from pdf_to_markdown_autogen.converter import PDFToMarkdownConverter
from pdf_to_markdown_autogen.config import get_config

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    config = get_config()
    
    # Initialize converter
    converter = PDFToMarkdownConverter(config)
    
    # Get PDF path from user
    pdf_path = input("Please enter the path to your PDF file: ")
    
    # Generate output path
    output_path = os.path.splitext(pdf_path)[0] + ".md"
    
    try:
        # Convert PDF to Markdown
        markdown_content = converter.convert(pdf_path, output_path)
        print(f"\nConversion completed successfully!")
        print(f"Output saved to: {output_path}")
    except Exception as e:
        print(f"\nError during conversion: {str(e)}")

if __name__ == "__main__":
    main() 