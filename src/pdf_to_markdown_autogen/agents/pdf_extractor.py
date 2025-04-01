from typing import Dict, Any, List, Tuple
import autogen
from pathlib import Path
import PyPDF2
import pdf2image
import os
import base64
from PIL import Image
import io

class PDFExtractorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are a PDF extraction specialist. Your role is to:
            1. Analyze PDF structure and content
            2. Extract text while preserving formatting
            3. Handle image extraction and placement
            4. Generate initial markdown""",
            llm_config=config
        )
    
    def extract_text(self, pdf_path: str) -> List[str]:
        """Extract text from PDF pages."""
        text_content = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text_content.append(page.extract_text())
        return text_content
    
    def extract_images(self, pdf_path: str, output_dir: Path) -> List[Tuple[str, str]]:
        """Extract images from PDF and save them."""
        images = []
        try:
            # Convert PDF pages to images
            pdf_images = pdf2image.convert_from_path(pdf_path)
            
            # Create images directory if it doesn't exist
            images_dir = output_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Save each page as an image
            for i, image in enumerate(pdf_images):
                image_path = images_dir / f"page_{i+1}.png"
                image.save(image_path)
                
                # Convert image to base64 for markdown
                with open(image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    images.append((f"page_{i+1}.png", img_data))
        
        except Exception as e:
            print(f"Warning: Could not extract images: {str(e)}")
        
        return images
    
    def process_content(self, text_content: List[str], images: List[Tuple[str, str]]) -> str:
        """Process extracted content using the AI agent."""
        # Prepare content for the agent
        content = {
            'text': text_content,
            'images': [name for name, _ in images]
        }
        
        # Get AI to process and format the content
        markdown = self.agent.generate_reply(
            messages=[{
                "role": "user",
                "content": f"Please convert this PDF content to markdown format. "
                          f"Text content: {text_content}\n"
                          f"Images: {[name for name, _ in images]}"
            }]
        )
        
        # Replace image placeholders with actual markdown
        for name, data in images:
            markdown = markdown.replace(
                f"[{name}]",
                f"![{name}](data:image/png;base64,{data})"
            )
        
        return markdown
    
    def extract_content(self, pdf_path: str) -> str:
        """Extract content from a PDF file."""
        pdf_path = Path(pdf_path)
        output_dir = pdf_path.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Extract text content
        text_content = self.extract_text(str(pdf_path))
        
        # Extract images
        images = self.extract_images(str(pdf_path), output_dir)
        
        # Process content using AI
        markdown_content = self.process_content(text_content, images)
        
        return markdown_content
