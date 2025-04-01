from typing import Dict, Any, List
import autogen
import re
import time
import logging

logger = logging.getLogger(__name__)

class MDValidatorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are a markdown validation specialist. Your role is to:
            1. Verify that ALL text from the original PDF is preserved exactly, with no omissions
            2. Ensure all tables are properly formatted in markdown using | and - characters
            3. Check that headings, lists, and formatting match the original document structure
            4. Verify that no content has been summarized or modified
            5. Confirm that all tables are in markdown format, not as images
            6. Validate that images are properly embedded and referenced
            7. If any content is missing or modified, reject the markdown and request regeneration
            8. Compare the length and structure of the original text with the markdown to ensure completeness""",
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
    
    def validate_markdown(self, markdown_content: str, original_text: List[str]) -> str:
        """Validate the generated markdown content."""
        # Prepare content for validation
        validation_prompt = f"""Please validate this markdown content against the original PDF text.
        This is a strict validation that requires exact preservation of all content.
        
        Check for:
        1. Text Preservation:
           - ALL text from the original must be present
           - No text should be omitted or summarized
           - Every paragraph and section must be preserved
           - Compare the length and structure to ensure completeness
        
        2. Table Formatting:
           - All tables must be in markdown format using | and - characters
           - No tables should be converted to images
           - Table structure and content must match the original exactly
        
        3. Document Structure:
           - Headings must match the original hierarchy exactly
           - Lists must maintain their original format and content
           - All sections must be in the correct order
           - No sections should be missing
        
        4. Images:
           - Only non-text images should be embedded
           - Tables must not be images
           - Image references must be valid
        
        If ANY content is missing or modified, respond with:
        "Critical Issues Found: [List the specific issues]"
        
        Original text:
        {original_text}
        
        Generated markdown:
        {markdown_content}
        
        Provide a detailed validation report focusing on content preservation and completeness."""
        
        try:
            # Get validation result from the agent
            validation_result = self.agent.generate_reply(
                messages=[{
                    "role": "user",
                    "content": validation_prompt
                }]
            )
            
            # Check for critical issues
            if "Critical Issues Found:" in validation_result:
                raise ValueError(f"Validation failed:\n{validation_result}")
            
            return validation_result
        except Exception as e:
            self._handle_rate_limit(e)
