from typing import Dict, Any, List
import autogen
import re
import time
import logging

logger = logging.getLogger(__name__)

class MDProcessorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="md_processor",
            system_message="""You are a markdown processing specialist. Your role is to:
            1. Convert PDF content to markdown while preserving ALL text exactly
            2. Format tables using markdown table syntax (| and - characters)
            3. Maintain the original document structure and hierarchy
            4. Preserve all formatting and special characters
            5. Keep all content without summarization or modification
            6. Handle images appropriately (only non-text images)
            7. Ensure tables are in markdown format, not images
            8. Preserve exact text content without any omissions""",
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
    
    def process_to_markdown(self, text_content: List[str], images: List[Dict[str, Any]]) -> str:
        """Convert the extracted text and images to markdown format."""
        # Prepare content for processing
        processing_prompt = f"""Convert this PDF content to markdown while preserving ALL text exactly.
        This is a strict conversion that requires exact preservation of all content.
        
        Requirements:
        1. Text Preservation:
           - Keep ALL text exactly as is
           - No omissions or summarization
           - Preserve every paragraph and section
           - Maintain exact wording and structure
        
        2. Table Formatting:
           - Convert all tables to markdown using | and - characters
           - Keep tables as markdown, not images
           - Preserve table structure and content exactly
        
        3. Document Structure:
           - Maintain original heading hierarchy
           - Keep all lists in their original format
           - Preserve section order
           - Include all sections
        
        4. Images:
           - Only embed non-text images
           - Keep tables as markdown
           - Use proper markdown image syntax
        
        Original text:
        {text_content}
        
        Images:
        {images}
        
        Generate markdown that preserves ALL content exactly."""
        
        try:
            # Get markdown from the agent
            markdown_content = self.agent.generate_reply(
                messages=[{
                    "role": "user",
                    "content": processing_prompt
                }]
            )
            
            return markdown_content
        except Exception as e:
            self._handle_rate_limit(e) 