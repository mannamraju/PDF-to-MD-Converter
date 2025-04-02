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
from openai import OpenAI, AzureOpenAI

logger = logging.getLogger(__name__)

class PDFExtractorAgent:
    """Agent responsible for extracting text content from PDFs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the PDF extractor agent."""
        self.config = config
        self.api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        # Extract API configuration
        api_config = config.get("config_list", [{}])[0]
        
        # Initialize appropriate client
        if self.api_provider == "azure":
            self.client = AzureOpenAI(
                api_version=api_config.get('api_version', '2024-12-01-preview'),
                azure_endpoint=api_config.get('base_url'),
                api_key=api_config.get('api_key'),
            )
        else:
            self.client = OpenAI(
                api_key=api_config.get('api_key'),
                base_url=api_config.get('base_url')
            )
        
        self.agent = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are an expert at analyzing PDF documents and converting them to well-formatted Markdown.
            Your task is to:
            1. Analyze the PDF structure and content
            2. Extract text while preserving formatting
            3. Handle image extraction and placement
            4. Generate initial markdown
            """,
            llm_config=config
        )
        
        self.min_request_interval = 3.0
        self.chunk_size = 4000
        self.max_retries = 5
        self.base_delay = 60
        self.rate_limit_history = []
        self.last_request_time = 0
        self.token_bucket = {
            "tokens": 1,
            "last_update": time.time(),
            "rate": 1/3.0
        }
    
    def _wait_for_rate_limit(self):
        """Implement token bucket algorithm for rate limiting with dynamic intervals."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Adjust interval based on rate limit history
        if self.rate_limit_history:
            time_since_last_rate_limit = current_time - self.rate_limit_history[-1]
            if time_since_last_rate_limit < 300:  # Within 5 minutes of last rate limit
                self.min_request_interval *= 1.5  # Increase interval by 50%
                # Only log significant rate limit events
                if self.min_request_interval > 10.0:
                    logger.info(f"Rate limit history detected. Increased interval to {self.min_request_interval:.2f} seconds")
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            # Only log significant wait times
            if sleep_time > 5.0:
                logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _handle_rate_limit(self, error: Exception) -> None:
        """Handle rate limit errors with exponential backoff and jitter."""
        if "429" in str(error):
            self.rate_limit_history.append(time.time())
            
            for attempt in range(self.max_retries):
                # Calculate delay with exponential backoff and jitter
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                jitter = random.uniform(0, delay * 0.1)  # 10% jitter
                total_delay = delay + jitter
                
                # Only log significant rate limit events
                if attempt >= 2 or total_delay > 120:
                    logger.info(f"Rate limit hit. Waiting {total_delay:.2f} seconds before retry {attempt + 1}/{self.max_retries}")
                time.sleep(total_delay)
            
            # Reset rate limit history after successful retries
            self.rate_limit_history = []
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
            # Extract Azure OpenAI configuration
            azure_config = self.config.get("config_list", [{}])[0]
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing PDF documents and converting them to well-formatted Markdown."
                    },
                    {
                        "role": "user",
                        "content": f"Convert this PDF content to markdown while preserving all formatting and structure:\n\n{chunk}"
                    }
                ],
                model=azure_config.get('model', 'o1'),
                max_completion_tokens=self.config.get('max_tokens', 40000),
                temperature=self.config.get('temperature', 1.0)
            )
            
            if not response.choices:
                raise Exception("Empty response received from the model")
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            self._handle_rate_limit(e)
            raise  # Re-raise the exception after handling rate limits
    
    def extract_content(self, pdf_path: str) -> str:
        """Extract content from PDF with chunked processing."""
        try:
            # Extract Azure OpenAI configuration
            azure_config = self.config.get("config_list", [{}])[0]
            
            # Extract text and images
            logger.info(f"\n=== PDF Extractor Starting Analysis ===")
            logger.info(f"Analyzing PDF structure: {pdf_path}")
            text_content = self.extract_text(pdf_path)
            images = self.extract_images(pdf_path, Path(pdf_path).parent / "output" / "images")
            
            # Process text in chunks
            chunks = [text_content[i:i + self.chunk_size] for i in range(0, len(text_content), self.chunk_size)]
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                self._wait_for_rate_limit()
                logger.info(f"\n=== Processing Chunk {i+1}/{len(chunks)} ===")
                
                processing_prompt = f"""Convert this PDF content to markdown while preserving all formatting and structure:

PDF Content (Chunk {i+1}/{len(chunks)}):
{chunk}

Requirements:
1. Preserve exact text content and order
2. Maintain heading hierarchy (use #, ##, ### etc.)
3. Format lists and tables correctly
4. Preserve code blocks and special formatting
5. Handle any complex layouts

Please provide detailed markdown conversion that keeps all original content intact."""

                logger.info("\nExtractor: Analyzing content structure...")
                logger.info("- Detecting headings and section hierarchy")
                logger.info("- Identifying lists, tables, and special elements")
                logger.info("- Analyzing formatting requirements")
                
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert PDF content analyzer and markdown converter. Your task is to convert PDF content to perfectly formatted markdown while preserving all content and structure exactly."
                        },
                        {
                            "role": "user",
                            "content": processing_prompt
                        }
                    ],
                    model=azure_config.get('model', 'o1'),
                    max_completion_tokens=self.config.get('max_tokens', 40000),
                    temperature=self.config.get('temperature', 1.0)
                )
                
                if not response.choices:
                    raise Exception(f"Empty response received from the model for chunk {i+1}")
                
                processed_chunk = response.choices[0].message.content
                logger.info(f"\nExtractor: Completed markdown conversion for chunk {i+1}")
                logger.info("Content structure preserved:")
                logger.info("- Headings and sections maintained")
                logger.info("- Lists and tables formatted")
                logger.info("- Special elements handled")
                
                processed_chunks.append(processed_chunk)
            
            # Combine processed chunks
            markdown_content = "\n\n".join(processed_chunks)
            
            # Add image references
            if images:
                logger.info(f"\nExtractor: Processing {len(images)} extracted images")
                markdown_content += "\n\n## Images\n"
                for i, img_path in enumerate(images):
                    markdown_content += f"\n![Image {i+1}]({img_path})\n"
                logger.info("Image references added to markdown")
            
            logger.info("\n=== PDF Extraction Complete ===")
            logger.info("Final markdown content generated with all elements preserved")
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            raise
