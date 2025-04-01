#!/usr/bin/env python3
import sys
from pathlib import Path
from src.pdf_to_markdown.processor import PDFProcessor

def get_pdf_path() -> str:
    """Get PDF file path from user input."""
    while True:
        print("\nPDF to Markdown Converter")
        print("=" * 30)
        path = input("\nEnter the path to your PDF file: ").strip()
        
        if not path:
            print("\nPath cannot be empty. Please try again.")
            continue
            
        path = str(Path(path).expanduser())
        if not Path(path).exists():
            print(f"\nFile not found: {path}")
            continue
            
        if not path.lower().endswith('.pdf'):
            print("\nFile must be a PDF. Please try again.")
            continue
            
        return path

def get_output_dir() -> str:
    """Get output directory from user input."""
    while True:
        output_dir = input("\nEnter output directory (press Enter for default 'output'): ").strip()
        
        if not output_dir:
            return "output"
            
        output_dir = str(Path(output_dir).expanduser())
        return output_dir

def main():
    try:
        # Get input from user
        pdf_path = get_pdf_path()
        output_dir = get_output_dir()
        
        print(f"\nProcessing PDF: {pdf_path}")
        print(f"Output directory: {output_dir}")
        
        # Process the PDF
        processor = PDFProcessor(pdf_path, output_dir)
        output_file = processor.process()
        
        if output_file:
            print(f"\nSuccessfully converted PDF to Markdown!")
            print(f"Output file: {output_file}")
            print(f"Log file: {Path(output_dir) / 'conversion.log'}")
        else:
            print("\nFailed to convert PDF to Markdown")
            print(f"Check the log file at: {Path(output_dir) / 'conversion.log'}")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    
    # Wait for user before exiting
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 