import os
from pathlib import Path
from .processor import PDFProcessor

def get_pdf_path() -> str:
    """Get PDF file path from user input."""
    while True:
        print("\nPDF to Markdown Converter")
        print("=" * 30)
        pdf_path = input("\nEnter the path to your PDF file: ").strip()
        
        if not pdf_path:
            print("\nPath cannot be empty. Please try again.")
            continue
            
        pdf_path = os.path.expanduser(pdf_path)  # Expand ~ to home directory
        if not os.path.exists(pdf_path):
            print(f"\nFile not found: {pdf_path}")
            continue
            
        if not pdf_path.lower().endswith('.pdf'):
            print("\nFile must be a PDF. Please try again.")
            continue
            
        return pdf_path

def main():
    try:
        # Get PDF path from user
        pdf_path = get_pdf_path()
        
        # Create output directory
        output_dir = "output"
        Path(output_dir).mkdir(exist_ok=True)
        
        # Process the PDF
        print("\nProcessing PDF...")
        processor = PDFProcessor(pdf_path, output_dir)
        output_file = processor.process()
        
        if output_file:
            print(f"\nSuccess! Markdown file created: {output_file}")
            print(f"Output directory: {output_dir}")
        else:
            print("\nFailed to convert PDF to markdown")
        
        # Wait for user to press return
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 