"""
Version tracking for the PDF to Markdown Converter solution.
Version format: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes or major architectural changes
- MINOR: New features or significant improvements
- PATCH: Bug fixes, minor improvements, and successful conversions
    - Auto-incremented after each successful PDF conversion
"""

__version__ = "2.1.0"

# Version history:
# 1.0.0 - Initial implementation with basic PDF to Markdown conversion
# 1.1.0 - Added strict validation criteria and character-by-character comparison
# 1.2.0 - Implemented sophisticated rate limit handling with dynamic intervals and exponential backoff
# 2.0.0 - Complete rewrite using AutoGen agents and added automatic version incrementing
# 2.1.0 - Enhanced markdown linting, documentation links, and formatting improvements