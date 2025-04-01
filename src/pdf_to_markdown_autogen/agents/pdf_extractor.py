from typing import Dict, Any, List, Tuple
import autogen
from pathlib import Path
import PyPDF2
import pdf2image
import os
import base64
from PIL import Image
import io
import cv2
import numpy as np

class PDFExtractorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are a PDF extraction specialist. Your role is to:
            1. Extract text exactly as it appears in the PDF, preserving all formatting
            2. Convert tables to markdown format using | and - characters
            3. Handle image extraction and placement
            4. Generate markdown that matches the original document structure exactly
            5. Do not summarize or modify the content in any way""",
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
    
    def detect_image_boundaries(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect boundaries of individual images in a page."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and sort contours by area
        image_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            # Filter out very small regions and regions that are too wide or tall
            if area > 1000 and w < image.shape[1] * 0.9 and h < image.shape[0] * 0.9:
                image_regions.append((x, y, w, h))
        
        # Sort regions from top to bottom, left to right
        image_regions.sort(key=lambda r: (r[1], r[0]))
        
        return image_regions
    
    def extract_images(self, pdf_path: str, output_dir: Path) -> List[Tuple[str, str]]:
        """Extract images from PDF and save them."""
        images = []
        try:
            # Convert PDF pages to images
            pdf_images = pdf2image.convert_from_path(pdf_path)
            
            # Create images directory if it doesn't exist
            images_dir = output_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Process each page
            for i, pil_image in enumerate(pdf_images):
                # Convert PIL image to OpenCV format
                cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                
                # Detect individual image boundaries
                regions = self.detect_image_boundaries(cv_image)
                
                # Extract and save each detected image
                for j, (x, y, w, h) in enumerate(regions):
                    # Extract the region
                    img_region = cv_image[y:y+h, x:x+w]
                    
                    # Convert back to PIL for saving
                    pil_region = Image.fromarray(cv2.cvtColor(img_region, cv2.COLOR_BGR2RGB))
                    
                    # Save the image
                    image_path = images_dir / f"page_{i+1}_image_{j+1}.png"
                    pil_region.save(image_path)
                    
                    # Convert image to base64 for markdown
                    with open(image_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                        images.append((f"page_{i+1}_image_{j+1}.png", img_data))
        
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
                "content": f"""Please convert this PDF content to markdown format, following these rules:
                1. Preserve all text exactly as it appears in the PDF
                2. Convert all tables to markdown format using | and - characters
                3. Keep all headings, lists, and formatting exactly as they appear
                4. Do not summarize or modify the content
                5. Include all tables in markdown format, not as images
                
                Text content: {text_content}
                Images: {[name for name, _ in images]}"""
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
