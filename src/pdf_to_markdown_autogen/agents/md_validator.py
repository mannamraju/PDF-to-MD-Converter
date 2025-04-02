from typing import Dict, Any, List
import autogen
import re
import time
import logging
import random

logger = logging.getLogger(__name__)

class MDValidatorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are a strict markdown validation specialist with zero tolerance for quality issues. Your role is to:
            1. Be extremely critical of any output that doesn't perfectly match the original
            2. Force the output agent to regenerate content if ANY issues are found
            3. Provide detailed, specific feedback about what needs to be fixed
            4. Use exact character-by-character comparison when needed
            5. Enforce strict markdown formatting rules
            6. Never accept partial or approximate matches
            7. Require perfect preservation of all formatting and structure
            8. Demand exact replication of tables, lists, and special characters""",
            llm_config=config
        )
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Increased minimum interval between requests
        self.max_validation_attempts = 3  # Maximum number of validation attempts per chunk
        self.rate_limit_count = 0  # Track rate limit occurrences
        self.last_rate_limit_time = 0  # Track last rate limit occurrence
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
    
    def _validate_content_length(self, markdown_content: str, original_text: List[str]) -> bool:
        """Validate that the markdown content length matches the original text."""
        markdown_length = len(markdown_content)
        original_length = sum(len(text) for text in original_text)
        length_diff = abs(markdown_length - original_length)
        length_threshold = original_length * 0.01  # 1% threshold
        
        if length_diff > length_threshold:
            logger.warning(f"Content length mismatch: markdown={markdown_length}, original={original_length}, diff={length_diff}")
            return False
        return True
    
    def _validate_table_formatting(self, markdown_content: str) -> bool:
        """Validate that tables are properly formatted in markdown."""
        # Check for table markers
        if "|" not in markdown_content:
            logger.warning("No table markers found in content")
            return False
        
        # Check for proper table structure
        table_lines = [line for line in markdown_content.split('\n') if '|' in line]
        if not table_lines:
            logger.warning("No properly formatted table lines found")
            return False
        
        # Check for header separator
        has_separator = any(all(c in line for c in ['-', '|']) for line in table_lines)
        if not has_separator:
            logger.warning("No table header separator found")
            return False
        
        return True
    
    def validate_markdown(self, markdown_content: str, original_text: str) -> bool:
        """Validate markdown content against original text with rate limit handling."""
        self._wait_for_rate_limit()
        
        try:
            validation_prompt = f"""Validate this markdown content against the original text with zero tolerance for errors.
            
            Original text:
            {original_text}
            
            Markdown content:
            {markdown_content}
            
            Requirements:
            1. Every character must match exactly
            2. All formatting must be preserved
            3. Structure must be identical
            4. No content should be lost or modified
            
            Provide detailed feedback if ANY issues are found."""
            
            response = self.agent.generate_reply(
                messages=[{
                    "role": "user",
                    "content": validation_prompt
                }]
            )
            
            # Check if validation passed
            if "issues found" in response.lower() or "error" in response.lower():
                logger.warning("Validation failed: " + response)
                return False
            
            return True
            
        except Exception as e:
            self._handle_rate_limit(e)
