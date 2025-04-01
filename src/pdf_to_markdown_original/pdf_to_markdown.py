import os
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import io
import base64
from pathlib import Path
import logging
from typing import List, Tuple, Optional

class PDFProcessor:
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def extract_text(self) -> List[str]:
        """Extract text from PDF pages."""
        text_content = []
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
            return text_content
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return []

    def extract_images(self) -> List[Tuple[str, str]]:
        """Extract images from PDF pages and save them."""
        image_data = []
        try:
            # Convert PDF to images
            images = convert_from_path(self.pdf_path)
            
            for i, image in enumerate(images):
                # Save image
                image_path = self.images_dir / f"page_{i+1}.png"
                image.save(image_path, "PNG")
                
                # Convert to base64 for markdown embedding
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                image_data.append((str(image_path), img_str))
            
            return image_data
        except Exception as e:
            self.logger.error(f"Error extracting images: {str(e)}")
            return []

    def create_markdown(self, text_content: List[str], image_data: List[Tuple[str, str]]) -> str:
        """Create markdown content from extracted text and images."""
        markdown_content = []
        
        for i, (text, (image_path, _)) in enumerate(zip(text_content, image_data)):
            # Add page number
            markdown_content.append(f"## Page {i+1}\n")
            
            # Add text content
            markdown_content.append(text)
            
            # Add image reference
            markdown_content.append(f"\n![Page {i+1}]({image_path})\n")
            
            # Add separator between pages
            markdown_content.append("---\n")
        
        return "\n".join(markdown_content)

    def process(self) -> Optional[str]:
        """Process PDF and create markdown output."""
        try:
            self.logger.info(f"Processing PDF: {self.pdf_path}")
            
            # Extract text and images
            text_content = self.extract_text()
            image_data = self.extract_images()
            
            if not text_content and not image_data:
                self.logger.error("No content extracted from PDF")
                return None
            
            # Create markdown content
            markdown_content = self.create_markdown(text_content, image_data)
            
            # Save markdown file
            output_file = self.output_dir / f"{Path(self.pdf_path).stem}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"Successfully created markdown file: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown with images')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output-dir', default='output', help='Output directory for markdown and images')
    
    args = parser.parse_args()
    
    processor = PDFProcessor(args.pdf_path, args.output_dir)
    output_file = processor.process()
    
    if output_file:
        print(f"Successfully converted PDF to markdown: {output_file}")
    else:
        print("Failed to convert PDF to markdown")

if __name__ == "__main__":
    main() 