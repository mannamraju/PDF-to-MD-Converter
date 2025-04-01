from typing import Dict, Any, List
import autogen
import re

class MDValidatorAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent = autogen.AssistantAgent(
            name="md_validator",
            system_message="""You are a markdown validation specialist. Your role is to:
            1. Verify that all text is preserved exactly as it appears in the original PDF
            2. Ensure all tables are properly formatted in markdown using | and - characters
            3. Check that headings, lists, and formatting match the original document structure
            4. Verify that no content has been summarized or modified
            5. Confirm that all tables are in markdown format, not as images
            6. Validate that images are properly embedded and referenced
            7. Report any discrepancies or issues found""",
            llm_config=config
        )
    
    def validate_markdown(self, markdown_content: str, original_text: List[str]) -> str:
        """Validate the generated markdown content."""
        # Prepare content for validation
        validation_prompt = f"""Please validate this markdown content against the original PDF text.
        Check for:
        1. Text Preservation:
           - All text should be exactly as it appears in the original
           - No summarization or modification of content
           - All paragraphs and sections should be preserved
        
        2. Table Formatting:
           - All tables should be in markdown format using | and - characters
           - No tables should be converted to images
           - Table structure and content should match the original
        
        3. Document Structure:
           - Headings should match the original hierarchy
           - Lists should maintain their original format
           - All sections should be in the correct order
        
        4. Images:
           - Only non-text images should be embedded
           - Tables should not be images
           - Image references should be valid
        
        Original text:
        {original_text}
        
        Generated markdown:
        {markdown_content}
        
        Please provide a detailed validation report, highlighting any issues found."""
        
        # Get validation from the agent
        validation_result = self.agent.generate_reply(
            messages=[{
                "role": "user",
                "content": validation_prompt
            }]
        )
        
        # Check for critical issues
        issues = []
        
        # Check for table images
        if "![table" in markdown_content.lower():
            issues.append("Found tables converted to images. Tables should be in markdown format.")
        
        # Check for missing tables
        if "|" not in markdown_content and any("|" in text for text in original_text):
            issues.append("Missing tables in markdown format. Tables should use | and - characters.")
        
        # Check for image references
        image_refs = re.findall(r'!\[(.*?)\]', markdown_content)
        if not image_refs:
            issues.append("No image references found. Check if images were properly extracted.")
        
        # Add any issues to the validation result
        if issues:
            validation_result = f"Critical Issues Found:\n" + "\n".join(issues) + "\n\n" + validation_result
        
        return validation_result
