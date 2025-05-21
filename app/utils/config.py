"""
Utility functions for logging and configuration.
"""
import logging
import os
from typing import Dict, Any
from app.utils.env import load_env_file, get_settings

# Load environment variables from settings.json file
load_env_file()

def setup_logging(log_level: str = "INFO", log_file: str = "app.log") -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create file handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    # Create console handler with appropriate encoding
    import sys
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Add the handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def get_app_config() -> Dict[str, Any]:
    """
    Get application configuration from settings.json file.
    
    Returns:
        Dict containing application configuration
    """
    # Get settings from file
    settings = get_settings()
    
    # If settings file exists, use those values, otherwise use environment variables with defaults
    if settings:
        return {
            "ollama_base_url": settings.get("ollama_base_url", "http://192.168.21.237:11434/"),
            "ollama_model": settings.get("ollama_model", "deepseek-r1:8b"),
            "temperature": float(settings.get("temperature", 0.1)),
            "chroma_persist_dir": settings.get("chroma_persist_dir", "./chroma_db"),
            "max_context": int(settings.get("max_context", 120)),
            "default_language": settings.get("default_language", "auto")
        }
    else:
        # Fallback to environment variables
        return {
            "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://192.168.21.237:11434/"),
            "ollama_model": os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b"),
            "temperature": float(os.environ.get("TEMPERATURE", "0.1")),
            "chroma_persist_dir": os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db"),
            "max_context": int(os.environ.get("MAX_CONTEXT", "120")),
            "default_language": os.environ.get("DEFAULT_LANGUAGE", "auto")
        }
