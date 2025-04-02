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
import random

logger = logging.getLogger(__name__)

class PDFExtractorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are a PDF content extraction specialist. Your role is to:
            1. Extract text content from PDFs while preserving structure and formatting
            2. Handle tables, lists, and special characters accurately
            3. Maintain the original document's hierarchy and organization
            4. Preserve all formatting and styling information
            5. Extract and handle images appropriately
            6. Ensure no content is lost or modified
            7. Keep the original text exactly as it appears
            8. Maintain document structure and layout""",
            llm_config=config
        )
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Increased minimum interval between requests
        self.max_validation_attempts = 3  # Maximum number of validation attempts per chunk
        self.rate_limit_count = 0  # Track rate limit occurrences
        self.last_rate_limit_time = 0  # Track last rate limit occurrence
        self.chunk_size = 2000  # Smaller chunk size for processing
        self.max_retries = 5  # Increased max retries
        self.base_delay = 60  # Base delay for rate limit handling
    
    def _wait_for_rate_limit(self):
        """Implement token bucket algorithm for rate limiting with dynamic intervals."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Adjust interval based on rate limit history
        if self.rate_limit_count > 0:
            time_since_last_rate_limit = current_time - self.last_rate_limit_time
            if time_since_last_rate_limit < 300:  # Within 5 minutes of last rate limit
                self.min_request_interval *= 1.5  # Increase interval by 50%
                logger.info(f"Rate limit history detected. Increased interval to {self.min_request_interval:.2f} seconds")
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _handle_rate_limit(self, error: Exception) -> None:
        """Handle rate limit errors with exponential backoff and jitter."""
        if "429" in str(error):
            self.rate_limit_count += 1
            self.last_rate_limit_time = time.time()
            
            for attempt in range(self.max_retries):
                # Calculate delay with exponential backoff and jitter
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                jitter = random.uniform(0, delay * 0.1)  # 10% jitter
                total_delay = delay + jitter
                
                logger.info(f"Rate limit hit. Waiting {total_delay:.2f} seconds before retry {attempt + 1}/{self.max_retries}")
                time.sleep(total_delay)
            
            # Reset rate limit count after successful retries
            self.rate_limit_count = 0
            raise Exception(f"Rate limit exceeded after {self.max_retries} retries")
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
    
    def _process_chunk(self, chunk: str) -> str:
        """Process a single chunk of text with rate limit handling."""
        self._wait_for_rate_limit()
        
        try:
            response = self.agent.generate_reply(
                messages=[{
                    "role": "user",
                    "content": f"Convert this PDF content to markdown while preserving all formatting and structure:\n\n{chunk}"
                }]
            )
            return response
        except Exception as e:
            self._handle_rate_limit(e)
    
    def extract_content(self, pdf_path: str) -> str:
        """Extract content from PDF with chunked processing."""
        try:
            # Extract text and images
            text_content = self.extract_text(pdf_path)
            images = self.extract_images(pdf_path, Path(pdf_path).parent / "output" / "images")
            
            # Process text in chunks
            chunks = [text_content[i:i + self.chunk_size] for i in range(0, len(text_content), self.chunk_size)]
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                processed_chunk = self._process_chunk(chunk)
                processed_chunks.append(processed_chunk)
            
            # Combine processed chunks
            markdown_content = "\n\n".join(processed_chunks)
            
            # Add image references
            if images:
                markdown_content += "\n\n## Images\n"
                for i, img_path in enumerate(images):
                    markdown_content += f"\n![Image {i+1}]({img_path})\n"
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            raise
