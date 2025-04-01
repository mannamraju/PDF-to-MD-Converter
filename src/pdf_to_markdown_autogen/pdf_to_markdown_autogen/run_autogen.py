import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pdf_to_markdown_autogen.ai_processor import AIProcessor

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

def main():
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get API provider choice from user
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
    
    # Initialize processor
    processor = AIProcessor()
    
    # Get PDF file path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("\nEnter the path to your PDF file: ").strip()
    
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)
    
    try:
        # Process the PDF
        output_file = processor.process(pdf_path)
        print(f"\nSuccessfully converted PDF to Markdown!")
        print(f"Output saved to: {output_file}")
    except Exception as e:
        print(f"\nError processing PDF: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 