"""
Language utilities for handling different languages in the QA system.
"""
import logging
import os
import re

# Set up logging
logger = logging.getLogger(__name__)

# Arabic-specific RTL markers
def is_arabic_text(text: str) -> bool:
    """
    Determine if the given text contains Arabic characters.
    
    Args:
        text: The text to check
        
    Returns:
        True if the text contains Arabic characters, False otherwise
    """
    # Check for Arabic Unicode character ranges
    return bool(re.search('[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))

RTL_MARK = "\u200F"  # Right-to-Left Mark
LTR_MARK = "\u200E"  # Left-to-Right Mark

def get_language_direction(language_code: str) -> str:
    """
    Get the text direction for a language code.
    
    Args:
        language_code: The language code (e.g., "english", "arabic")
        
    Returns:
        "rtl" for Right-to-Left languages, "ltr" for Left-to-Right languages
    """
    rtl_languages = ["arabic", "hebrew", "urdu", "farsi", "persian"]
    return "rtl" if language_code.lower() in rtl_languages else "ltr"

def format_text_for_direction(text: str) -> str:
    """
    Format text according to its language direction.
    
    Args:
        text: The text to format
        
    Returns:
        Formatted text with appropriate direction marks
    """
    # Auto-detect language if not provided
    language_code = "arabic" if is_arabic_text(text) else "english"
        
    direction = get_language_direction(language_code)
    
    if direction == "rtl":
        return f"{RTL_MARK}{text}"
    else:
        return f"{LTR_MARK}{text}"

def get_default_language() -> str:
    """
    Get the default language from configuration.
    
    Returns:
        Language code (e.g., "english", "arabic", "auto")
    """
    # Get default language from environment variable
    default_language = os.environ.get("DEFAULT_LANGUAGE", "auto").lower()
    
    # If auto, return "auto", otherwise ensure it's a valid language
    if default_language == "auto":
        return default_language
        
    # Ensure the language is valid
    valid_languages = ["english", "arabic"]
    if default_language in valid_languages:
        return default_language
    
    # Default to English if invalid language is specified
    logger.warning(f"Invalid default language: {default_language}. Using English instead.")
    return "english"
