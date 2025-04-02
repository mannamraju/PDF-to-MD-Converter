from typing import Dict, Any, List, Tuple
import autogen
import re
import time
import logging
import random
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class MDValidatorAgent:
    """Agent responsible for validating markdown content."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the markdown validator agent."""
        self.config = config
        
        # Extract Azure OpenAI configuration
        azure_config = config.get("config_list", [{}])[0]
        self.client = AzureOpenAI(
            api_version=azure_config.get('api_version', '2024-12-01-preview'),
            azure_endpoint=azure_config.get('azure_endpoint'),
            api_key=azure_config.get('api_key'),
        )
        
        self.agent = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are an expert at validating markdown content.
            Your task is to:
            1. Compare markdown content with original text
            2. Ensure all content is preserved
            3. Verify formatting is correct
            4. Report any discrepancies
            """,
            llm_config=config
        )
        
        self.min_request_interval = 3.0
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
    
    def _split_into_semantic_chunks(self, content: str, max_tokens: int = 150000) -> List[str]:
        """Split content into semantic chunks (by sections/paragraphs) respecting token limits."""
        # Split on major section boundaries first
        sections = re.split(r'\n#+\s', content)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        estimated_tokens_per_char = 1.5  # Conservative estimate
        
        for section in sections:
            # Rough token estimate for this section
            section_tokens = len(section) * estimated_tokens_per_char
            
            if current_tokens + section_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section
                current_tokens = section_tokens
            else:
                if current_chunk:
                    current_chunk += "\n# " + section
                else:
                    current_chunk = section
                current_tokens += section_tokens
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def validate_markdown(self, markdown_content: str, original_text: str) -> Tuple[bool, str]:
        """Validate markdown content against original text."""
        try:
            # Extract Azure OpenAI configuration
            azure_config = self.config.get("config_list", [{}])[0]
            
            # Split content into semantic chunks with token limit consideration
            md_chunks = self._split_into_semantic_chunks(markdown_content)
            orig_chunks = self._split_into_semantic_chunks(original_text)
            
            # Use the smaller number of chunks to avoid index errors
            num_chunks = min(len(md_chunks), len(orig_chunks))
            
            if num_chunks > 1:
                logger.info(f"Content split into {num_chunks} semantic chunks for validation")
            
            validation_results = []
            has_discrepancies = False
            
            # Validate each chunk
            for i in range(num_chunks):
                self._wait_for_rate_limit()
                logger.info(f"\n=== Starting validation of chunk {i + 1}/{num_chunks} ===")
                logger.info("\nValidator: Analyzing markdown structure and content...")
                
                validation_prompt = f"""Compare this section of markdown content with the original text and report any discrepancies:

Markdown Content (Section {i + 1}/{num_chunks}):
{md_chunks[i]}

Original Text (Section {i + 1}/{num_chunks}):
{orig_chunks[i]}

Please provide a detailed analysis focusing on:
1. Content completeness - is all original text preserved?
2. Structure accuracy - are headings, lists, and tables formatted correctly?
3. Formatting consistency - is markdown syntax used properly?
4. Special elements - are code blocks, links, and images handled correctly?

Format your response as:
CONTENT: [analysis of content preservation]
STRUCTURE: [analysis of structural elements]
FORMATTING: [analysis of markdown syntax]
SPECIAL_ELEMENTS: [analysis of special content]
ISSUES: [list any discrepancies found]
"""
                
                logger.info("\nValidator: Sending validation request to AI model...")
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert markdown validator. Your task is to perform a detailed analysis of markdown conversion accuracy, comparing the converted markdown against the original text. Be thorough and specific in your analysis."
                        },
                        {
                            "role": "user",
                            "content": validation_prompt
                        }
                    ],
                    model=azure_config.get('model', 'o1'),
                    max_completion_tokens=self.config.get('max_tokens', 40000),
                    temperature=self.config.get('temperature', 0.7)
                )
                
                if not response.choices:
                    raise Exception(f"Empty response received from the model for chunk {i + 1}")
                
                result = response.choices[0].message.content
                logger.info(f"\nValidator Analysis for Chunk {i + 1}:\n{result}")
                validation_results.append(result)
                
                # Check for discrepancies in this chunk
                if "discrepancy" in result.lower() or "missing" in result.lower():
                    has_discrepancies = True
                    logger.warning(f"\nDiscrepancies found in chunk {i + 1}")
            
            # Combine validation results
            combined_result = "\n\n=== Complete Validation Results ===\n\n" + "\n\n---\n\n".join(validation_results)
            
            if has_discrepancies:
                logger.warning("\nValidation complete: Issues found in the conversion")
            else:
                logger.info("\nValidation complete: No significant issues found")
            
            return not has_discrepancies, combined_result
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return False, f"Error during validation: {str(e)}"
