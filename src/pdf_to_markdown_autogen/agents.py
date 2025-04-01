from typing import Dict, List, Tuple
import autogen
from pathlib import Path
import PyPDF2
import io
from PIL import Image
import logging
from pdf_to_markdown_autogen.config import api_config

class PDFExtractorAgent:
    """Agent responsible for extracting content from PDFs."""
    
    def __init__(self, config_list: List[Dict]):
        self.config_list = config_list
        config = {
            "model": "gpt-3.5-turbo" if not api_config.is_azure else "gpt-4"
        }
        
        if api_config.is_azure:
            config = {
                "config_list": [{
                    "model": "gpt-4o",
                    "base_url": f"{api_config.api_base}/openai/deployments/gpt-4o/chat/completions",
                    "api_key": api_config.api_key,
                    "api_type": "azure"
                }]
            }
        
        self.assistant = autogen.AssistantAgent(
            name="pdf_extractor",
            system_message="""You are an expert at analyzing PDF documents and converting them to well-formatted Markdown.
            Your task is to:
            1. Analyze the PDF structure and content
            2. Extract text while preserving formatting
            3. Handle image extraction and placement
            4. Generate initial markdown
            """,
            llm_config={
                "config_list": [config],
                "temperature": 0.7
            }
        )
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "output", "use_docker": False},
            llm_config={
                "config_list": [config],
                "temperature": 0.7
            }
        )
    
    def extract_content(self, pdf_path: str) -> str:
        """Extract content from PDF using the assistant agent."""
        try:
            # Read PDF content
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n\n"
            
            # Create a chat to process the content
            self.user_proxy.initiate_chat(
                self.assistant,
                message=f"""Please convert this PDF content to well-formatted Markdown:

{text_content}

Follow these guidelines:
1. Preserve headings, lists, and other structural elements
2. Maintain proper formatting and hierarchy
3. Handle any special characters or symbols appropriately
4. Include proper line breaks and spacing

Please provide the Markdown content directly without any additional commentary.
TERMINATE"""
            )
            
            # Get the last message from the assistant
            chat_history = self.user_proxy.chat_messages[self.assistant.name]
            if not chat_history:
                raise ValueError("No response received from the assistant")
            
            markdown_content = chat_history[-1]["content"]
            return markdown_content
            
        except Exception as e:
            logging.error(f"Error extracting content: {str(e)}")
            raise

class MDValidatorAgent:
    """Agent responsible for validating generated markdown."""
    
    def __init__(self, config_list: List[Dict]):
        self.config_list = config_list
        config = {
            "model": "gpt-3.5-turbo" if not api_config.is_azure else "gpt-4"
        }
        
        if api_config.is_azure:
            config = {
                "config_list": [{
                    "model": "gpt-4o",
                    "base_url": f"{api_config.api_base}/openai/deployments/gpt-4o/chat/completions",
                    "api_key": api_config.api_key,
                    "api_type": "azure"
                }]
            }
        
        self.assistant = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are an expert at validating Markdown documents against their source PDFs.
            Your task is to:
            1. Validate generated markdown against the original PDF
            2. Check structure accuracy
            3. Verify content completeness
            4. Ensure proper formatting
            5. Report any issues
            """,
            llm_config={
                "config_list": [config],
                "temperature": 0.3
            }
        )
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "output", "use_docker": False},
            llm_config={
                "config_list": [config],
                "temperature": 0.3
            }
        )
    
    def validate_markdown(self, pdf_path: str, markdown_content: str) -> Tuple[bool, str]:
        """Validate the generated markdown against the original PDF."""
        try:
            # Read PDF content for comparison
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n\n"
            
            # Create a chat to validate the content
            self.user_proxy.initiate_chat(
                self.assistant,
                message=f"""Please validate this Markdown content against the original PDF content.

Original PDF content:
{pdf_text}

Generated Markdown:
{markdown_content}

Please analyze and report:
1. Is the content complete and accurate?
2. Are all headings preserved correctly?
3. Is the formatting maintained properly?
4. Are there any missing or incorrect elements?

Respond with a JSON-like format:
{{
    "is_valid": true/false,
    "report": "detailed validation report"
}}
TERMINATE"""
            )
            
            # Get the last message from the assistant
            chat_history = self.user_proxy.chat_messages[self.assistant.name]
            if not chat_history:
                raise ValueError("No response received from the assistant")
            
            # Parse the response
            response = chat_history[-1]["content"]
            # Simple parsing - in real implementation, use json.loads with proper error handling
            is_valid = '"is_valid": true' in response.lower()
            report = response
            
            return is_valid, report
            
        except Exception as e:
            logging.error(f"Error validating markdown: {str(e)}")
            raise 