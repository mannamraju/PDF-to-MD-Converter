import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .ai_processor import AIProcessor

def get_api_provider():
    """Ask user to choose API provider and wait for confirmation."""
    while True:
        print("\nChoose your API provider:")
        print("1. OpenAI")
        print("2. Azure OpenAI")
        
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            provider = "openai"
        elif choice == "2":
            provider = "azure"
        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue
        
        print(f"\nYou selected: {provider.upper()}")
        confirm = input("Press Enter to confirm or 'n' to change: ").strip().lower()
        
        if confirm != 'n':
            return provider
        print("\nLet's try again...")

def get_pdf_path() -> str:
    """Get PDF file path from user input."""
    while True:
        print("\nPDF to Markdown Converter (AutoGen Version)")
        print("=" * 40)
        print("\nPlease enter the full path to your PDF file.")
        print("Example: /Users/username/Documents/document.pdf")
        print("Press Enter to cancel.")
        path = input("\nPDF file path: ").strip()
        
        if not path:
            print("\nOperation cancelled by user.")
            sys.exit(0)
            
        path = str(Path(path).expanduser())
        if not Path(path).exists():
            print(f"\nError: File not found: {path}")
            print("Please check the path and try again.")
            continue
            
        if not path.lower().endswith('.pdf'):
            print("\nError: File must be a PDF.")
            print("Please select a PDF file and try again.")
            continue
            
        print(f"\nSelected file: {path}")
        confirm = input("Press Enter to confirm or 'n' to change: ").strip().lower()
        
        if confirm != 'n':
            return path
        print("\nLet's try again...")

def main():
    # Load environment variables
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
    
    # Only ask for API provider if not already set
    current_provider = os.getenv('API_PROVIDER')
    if not current_provider:
        provider = get_api_provider()
        
        # Update .env file with user's choice
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('API_PROVIDER='):
                    f.write(f'API_PROVIDER={provider}\n')
                else:
                    f.write(line)
        
        print(f"\nAPI provider set to: {provider.upper()}")
    else:
        print(f"\nUsing existing API provider: {current_provider.upper()}")
    
    # Get PDF file path from user
    pdf_path = get_pdf_path()
    
    # Process the PDF
    processor = AIProcessor(pdf_path)
    output_file = processor.process()
    
    print(f"\nConversion complete! Output saved to: {output_file}")

if __name__ == "__main__":
    main() 