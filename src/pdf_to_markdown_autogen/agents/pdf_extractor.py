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
import time
import logging

logger = logging.getLogger(__name__)

class PDFExtractorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are a PDF extraction specialist. Your role is to:
            1. Extract ALL text exactly as it appears in the PDF, preserving every word and section
            2. Convert tables to markdown format using | and - characters
            3. Handle image extraction and placement
            4. Generate markdown that matches the original document structure exactly
            5. Do not summarize or modify the content in any way
            6. Ensure no content is omitted or lost during conversion
            7. Preserve all formatting, including bold, italic, and other text styles
            8. Maintain exact section hierarchy and document structure""",
            llm_config=config
        )
    
    def _handle_rate_limit(self, error: Exception, max_retries: int = 3) -> None:
        """Handle rate limit errors with exponential backoff."""
        if "429" in str(error):
            retry_delay = 60  # Start with 60 seconds
            for attempt in range(max_retries):
                logger.info(f"Rate limit hit. Waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            raise Exception(f"Rate limit exceeded after {max_retries} retries")
        raise error
    
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
            # Filter out very small regions that are likely text
            if w * h > 100:  # Minimum area threshold
                image_regions.append((x, y, w, h))
        
        return sorted(image_regions, key=lambda r: (r[1], r[0]))  # Sort by y, then x
    
    def extract_images(self, pdf_path: str, output_dir: Path) -> List[Tuple[str, str]]:
        """Extract images from PDF pages."""
        images = []
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF pages to images
        pdf_images = pdf2image.convert_from_path(pdf_path)
        
        for i, page_image in enumerate(pdf_images):
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
            
            # Detect image boundaries
            regions = self.detect_image_boundaries(cv_image)
            
            for j, (x, y, w, h) in enumerate(regions):
                # Extract individual image
                img = cv_image[y:y+h, x:x+w]
                
                # Convert back to PIL for saving
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                
                # Save image
                img_path = output_dir / f"image_{i+1}_{j+1}.png"
                pil_img.save(img_path)
                
                # Convert to base64 for markdown
                buffered = io.BytesIO()
                pil_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                images.append((str(img_path), img_str))
        
        return images
    
    def process_content(self, text_content: List[str], images: List[Tuple[str, str]], preserve_all: bool = True) -> str:
        """Process extracted content into markdown format."""
        # Prepare content for processing
        processing_prompt = f"""Convert this PDF content to markdown format.
        Requirements:
        1. Preserve ALL text exactly as it appears
        2. Convert tables to markdown format using | and - characters
        3. Maintain exact document structure and hierarchy
        4. Do not summarize or modify any content
        5. Preserve all formatting and styles
        6. Ensure no content is omitted
        
        Original text:
        {text_content}
        
        Images (base64 encoded):
        {images}
        
        Generate markdown that preserves all content exactly."""
        
        try:
            # Get markdown content from the agent
            markdown_content = self.agent.generate_reply(
                messages=[{
                    "role": "user",
                    "content": processing_prompt
                }]
            )
            return markdown_content
        except Exception as e:
            self._handle_rate_limit(e)
    
    def extract_content(self, pdf_path: str, preserve_all: bool = True) -> str:
        """Extract and process content from PDF."""
        # Extract text and images
        text_content = self.extract_text(pdf_path)
        images = self.extract_images(pdf_path, Path(pdf_path).parent / "output" / "images")
        
        # Process content into markdown
        return self.process_content(text_content, images, preserve_all)
