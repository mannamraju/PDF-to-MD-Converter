import os
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import io
import base64
from pathlib import Path
import logging
from typing import List, Tuple, Optional
import re
from urllib.parse import quote

class PDFProcessor:
    VERSION = "1.1.0"  # Version number for the processor
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Setup logging to both file and console
        log_file = self.output_dir / "conversion.log"
        
        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info(f"Initialized PDF processor v{self.VERSION} for: {pdf_path}")
        self.logger.info(f"Output directory: {self.output_dir}")

    def _detect_heading_level(self, line: str) -> Optional[int]:
        """Detect heading level based on text characteristics."""
        line = line.strip()
        
        # Check for specific heading patterns
        if line.startswith('## '):
            self.logger.info(f"Detected heading level 2 (##) from pattern: {line}")
            return 2
        if line.startswith('### '):
            self.logger.info(f"Detected heading level 3 (###) from pattern: {line}")
            return 3
            
        # Check for common heading patterns
        if re.match(r'^[A-Z][A-Z\s]{10,}$', line):  # All caps with spaces
            self.logger.info(f"Detected heading level 1 (#) from all-caps pattern: {line}")
            return 1
        if re.match(r'^[A-Z][a-z\s]{10,}$', line):  # Title case
            self.logger.info(f"Detected heading level 2 (##) from title case pattern: {line}")
            return 2
        if re.match(r'^[A-Z][a-z\s]{5,}$', line):   # Shorter title case
            self.logger.info(f"Detected heading level 3 (###) from short title case pattern: {line}")
            return 3
            
        # Check for common heading indicators
        if line.endswith(':'):
            self.logger.warning(f"Making assumption: treating line ending with colon as heading level 3: {line}")
            return 3
        if line.endswith('.'):
            self.logger.warning(f"Making assumption: treating line ending with period as heading level 3: {line}")
            return 3
            
        # Check for common heading words
        heading_words = ['overview', 'background', 'description', 'summary', 'findings', 'resources']
        if any(word in line.lower() for word in heading_words):
            self.logger.warning(f"Making assumption: treating line with common heading word as level 2: {line}")
            return 2
            
        return None

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text by removing email addresses and making company references generic."""
        # Remove email addresses
        original_text = text
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[email]', text)
        if text != original_text:
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', original_text)
            for email in emails:
                self.logger.info(f"Filtered out email address: {email}")
        
        # Replace company websites (except Microsoft)
        original_text = text
        text = re.sub(r'https?://(?!microsoft\.com)[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}', '[company website]', text)
        if text != original_text:
            websites = re.findall(r'https?://(?!microsoft\.com)[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}', original_text)
            for website in websites:
                self.logger.info(f"Filtered out company website: {website}")
        
        # Replace company names with generic terms
        company_patterns = [
            r'\b[A-Z][a-zA-Z]+(?:\.com|\.org|\.net|\.io|\.ai|\.tech)\b',
            r'\b[A-Z][a-zA-Z]+(?: Inc\.| LLC| Ltd\.| Corporation| Corp\.)\b'
        ]
        
        for pattern in company_patterns:
            original_text = text
            text = re.sub(pattern, '[Company]', text)
            if text != original_text:
                companies = re.findall(pattern, original_text)
                for company in companies:
                    self.logger.info(f"Filtered out company name: {company}")
        
        return text

    def _process_text(self, text: str) -> str:
        """Process extracted text to handle special formatting."""
        # First sanitize the text
        text = self._sanitize_text(text)
        
        lines = text.split('\n')
        processed_lines = []
        in_table = False
        table_lines = []
        in_list = False
        current_section = None
        skip_toc = False
        list_content = []
        
        # Check if this is a table of contents page
        toc_indicators = [
            "table of contents",
            "contents",
            "page",
            "chapter",
            "section"
        ]
        
        # Look for TOC indicators in the first few lines
        first_lines = [line.lower().strip() for line in lines[:5]]
        if any(indicator in " ".join(first_lines) for indicator in toc_indicators):
            self.logger.info("Detected table of contents page - skipping content")
            skip_toc = True
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                if in_table:
                    # Process collected table lines
                    processed_lines.extend(self._process_table(table_lines))
                    table_lines = []
                    in_table = False
                if in_list:
                    # Process collected list lines
                    processed_lines.extend(self._process_list(list_content))
                    list_content = []
                    in_list = False
                continue
            
            # Skip table of contents
            if skip_toc:
                # Check if we've reached the end of TOC (usually marked by a main heading)
                if re.match(r'^[A-Z][A-Z\s]{10,}$', line) or re.match(r'^[A-Z][a-z\s]{10,}$', line):
                    self.logger.info(f"Reached end of table of contents at line: {line}")
                    skip_toc = False
                else:
                    continue
            
            # Detect and process headings
            heading_level = self._detect_heading_level(line)
            if heading_level:
                if heading_level == 2:
                    current_section = line
                    self.logger.info(f"New section started: {line}")
                markdown_heading = f"{'#' * heading_level} {line}"
                processed_lines.append(markdown_heading)
                self.logger.info(f"Converted heading to markdown: {markdown_heading}")
                continue
            
            # Handle bullet points and numbered lists
            bullet_match = re.match(r'^[\s•\-\*]+(.*)', line)
            if bullet_match:
                content = bullet_match.group(1).strip()
                if content:
                    list_content.append(content)
                    in_list = True
                continue
                
            number_match = re.match(r'^(\d+\.)\s+(.*)', line)
            if number_match:
                number, content = number_match.groups()
                if content:
                    list_content.append(f"{number}. {content}")
                    in_list = True
                continue
            
            # Handle tables
            if '  ' in line or '\t' in line:
                if not in_table:
                    self.logger.warning(f"Making assumption: treating text with multiple spaces/tabs as table: {line}")
                    in_table = True
                table_lines.append(line)
                continue
            
            # Process regular text
            if in_table:
                # Process collected table lines
                processed_lines.extend(self._process_table(table_lines))
                table_lines = []
                in_table = False
            
            # Add regular text with proper spacing
            if line:
                if not in_list:
                    processed_lines.append(line)
                else:
                    # Check if this is a continuation of the previous list item
                    if line.startswith('  ') or line.startswith('\t'):
                        list_content[-1] += ' ' + line.strip()
                    else:
                        # Process the list and start a new paragraph
                        processed_lines.extend(self._process_list(list_content))
                        list_content = []
                        in_list = False
                        processed_lines.append(line)
        
        # Process any remaining table lines
        if table_lines:
            processed_lines.extend(self._process_table(table_lines))
            
        # Process any remaining list lines
        if list_content:
            processed_lines.extend(self._process_list(list_content))
        
        return '\n'.join(processed_lines)

    def _process_table(self, lines: List[str]) -> List[str]:
        """Process table lines into markdown table format."""
        if not lines:
            return []
            
        # Split lines into columns and clean up
        table_data = []
        for line in lines:
            # Split on multiple spaces or tabs
            columns = re.split(r'\s{2,}|\t', line)
            # Clean up each column
            columns = [col.strip() for col in columns if col.strip()]
            if columns:
                table_data.append(columns)
        
        if not table_data:
            return []
        
        # Log table structure assumptions
        if len(table_data) > 1:
            self.logger.warning(f"Making assumption: treating first row as header: {table_data[0]}")
            if len(table_data[0]) != len(table_data[1]):
                self.logger.warning(f"Warning: Inconsistent column count in table. Header: {len(table_data[0])}, Data: {len(table_data[1])}")
        
        # Create markdown table
        markdown_lines = []
        
        # Add header row
        header = ' | '.join(table_data[0])
        markdown_lines.append(f"| {header} |")
        
        # Add separator row
        separator = ' | '.join(['---' for _ in table_data[0]])
        markdown_lines.append(f"| {separator} |")
        
        # Add data rows
        for row in table_data[1:]:
            if len(row) == len(table_data[0]):  # Only add rows with matching column count
                row_text = ' | '.join(row)
                markdown_lines.append(f"| {row_text} |")
            else:
                self.logger.warning(f"Skipping table row due to column count mismatch: {row}")
        
        return markdown_lines

    def _process_list(self, items: List[str]) -> List[str]:
        """Process list items into markdown format."""
        if not items:
            return []
            
        markdown_lines = []
        for item in items:
            # Handle bold text
            if '**' in item:
                markdown_lines.append(f"- {item}")
            else:
                markdown_lines.append(f"- {item}")
        
        return markdown_lines

    def extract_text(self) -> List[str]:
        """Extract text from PDF pages."""
        text_content = []
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    processed_text = self._process_text(text)
                    text_content.append(processed_text)
            return text_content
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return []

    def extract_images(self) -> List[Tuple[str, str]]:
        """Extract images from PDF pages and save them."""
        image_data = []
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    # Extract images from the page
                    if '/XObject' in page['/Resources']:
                        x_objects = page['/Resources']['/XObject'].get_object()
                        
                        for obj in x_objects:
                            if x_objects[obj]['/Subtype'] == '/Image':
                                image = x_objects[obj]
                                
                                try:
                                    # Log image properties for debugging
                                    self.logger.info(f"Processing image on page {page_num + 1}")
                                    self.logger.info(f"Image properties: {image}")
                                    
                                    # Get image dimensions
                                    width = image['/Width']
                                    height = image['/Height']
                                    
                                    # Get image data
                                    if '/Filter' in image:
                                        filter_type = image['/Filter']
                                        self.logger.info(f"Image filter type: {filter_type}")
                                        
                                        # Get the raw image data
                                        image_data_bytes = image.get_data()
                                        
                                        # Handle different image formats
                                        if filter_type == '/DCTDecode':
                                            # JPEG image
                                            img = Image.open(io.BytesIO(image_data_bytes))
                                        elif filter_type == '/FlateDecode':
                                            # PNG image
                                            try:
                                                # First try to open as PNG
                                                img = Image.open(io.BytesIO(image_data_bytes))
                                            except Exception as e:
                                                self.logger.warning(f"Failed to open FlateDecode image as PNG: {str(e)}")
                                                # If that fails, try to create from raw data
                                                try:
                                                    # Get color mode
                                                    if '/ColorSpace' in image:
                                                        if isinstance(image['/ColorSpace'], list):
                                                            color_space = image['/ColorSpace'][0]
                                                        else:
                                                            color_space = image['/ColorSpace']
                                                            
                                                        if color_space == '/DeviceRGB':
                                                            mode = 'RGB'
                                                        elif color_space == '/DeviceGray':
                                                            mode = 'L'
                                                        elif color_space == '/DeviceCMYK':
                                                            mode = 'CMYK'
                                                        else:
                                                            mode = 'RGB'  # Default to RGB
                                                    else:
                                                        mode = 'RGB'  # Default to RGB
                                                    
                                                    # Create image from raw data
                                                    img = Image.frombytes(mode, (width, height), image_data_bytes)
                                                except Exception as e:
                                                    self.logger.error(f"Failed to create image from raw data: {str(e)}")
                                                    continue
                                        elif filter_type == '/JPXDecode':
                                            # JPEG2000 image
                                            img = Image.open(io.BytesIO(image_data_bytes))
                                        elif filter_type == '/CCITTFaxDecode':
                                            # TIFF/CCITT image
                                            img = Image.open(io.BytesIO(image_data_bytes))
                                        else:
                                            self.logger.warning(f"Unsupported image filter: {filter_type}")
                                            continue
                                        
                                        # Handle ICC color profile if present
                                        if '/ColorSpace' in image and isinstance(image['/ColorSpace'], list):
                                            if image['/ColorSpace'][0] == '/ICCBased':
                                                try:
                                                    icc_profile = image['/ColorSpace'][1].get_data()
                                                    img.info['icc_profile'] = icc_profile
                                                except Exception as e:
                                                    self.logger.warning(f"Could not extract ICC profile: {str(e)}")
                                        
                                        # Handle soft mask (transparency) if present
                                        if '/SMask' in image:
                                            try:
                                                mask = image['/SMask'].get_object()
                                                mask_data = mask.get_data()
                                                mask_img = Image.open(io.BytesIO(mask_data))
                                                if mask_img.mode == 'L':
                                                    img.putalpha(mask_img)
                                            except Exception as e:
                                                self.logger.warning(f"Could not apply soft mask: {str(e)}")
                                        
                                        # Convert to RGBA if needed, preserving white background
                                        if img.mode not in ('RGB', 'RGBA'):
                                            if img.mode == 'L':  # Grayscale
                                                img = img.convert('RGBA')
                                                # Create a white background
                                                background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                                                # Composite the image onto the white background
                                                img = Image.alpha_composite(background, img)
                                            elif img.mode == 'CMYK':
                                                img = img.convert('RGB')
                                                # Create a white background
                                                background = Image.new('RGB', img.size, (255, 255, 255))
                                                # Composite the image onto the white background
                                                img = Image.composite(img, background, img)
                                            else:
                                                img = img.convert('RGBA')
                                                # Create a white background
                                                background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                                                # Composite the image onto the white background
                                                img = Image.alpha_composite(background, img)
                                        
                                        # Ensure white background for transparent images
                                        if img.mode == 'RGBA':
                                            # Create a white background
                                            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                                            # Composite the image onto the white background
                                            img = Image.alpha_composite(background, img)
                                        
                                        # Generate unique filename
                                        image_filename = f"image_{page_num + 1}_{len(image_data) + 1}.png"
                                        image_path = self.images_dir / image_filename
                                        
                                        # Save image
                                        try:
                                            img.save(image_path, "PNG")
                                            self.logger.info(f"Successfully saved image: {image_filename}")
                                        except Exception as e:
                                            self.logger.error(f"Error saving image {image_filename}: {str(e)}")
                                            continue
                                        
                                        # Store relative path using ../output/images/ prefix
                                        relative_path = f"../output/images/{image_filename}"
                                        image_data.append((relative_path, f"Image from page {page_num + 1}"))
                                        
                                    else:
                                        self.logger.warning("Image has no filter type, skipping")
                                        continue
                                    
                                except Exception as e:
                                    self.logger.error(f"Error processing image on page {page_num + 1}: {str(e)}")
                                    self.logger.error(f"Image properties: {image}")
                                    continue
            
            return image_data
        except Exception as e:
            self.logger.error(f"Error extracting images: {str(e)}")
            return []

    def create_markdown(self, text_content: List[str], image_data: List[Tuple[str, str]]) -> str:
        """Create markdown content from extracted text and images."""
        markdown_content = []
        
        # Add version information at the top
        markdown_content.append(f"<!-- Generated by PDF to Markdown Converter v{self.VERSION} -->\n")
        
        # Process text content
        for i, text in enumerate(text_content):
            # Add text content
            markdown_content.append(text)
            
            # Find images that belong to this page
            page_images = [(path, alt) for path, alt in image_data if f"image_{i+1}_" in path]
            
            # Add image references for this page
            if page_images:
                markdown_content.append("\n### Images from this page\n")
                for image_path, alt_text in page_images:
                    markdown_content.append(f"![{alt_text}]({image_path})\n")
            
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