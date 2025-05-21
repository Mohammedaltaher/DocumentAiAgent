"""
LLM utility module.
This module provides functions for working with language models.
"""
from fastapi import HTTPException
from langchain_ollama import OllamaLLM
import logging

from app.utils.config import get_app_config

# Set up logging
logger = logging.getLogger(__name__)

# Get application configuration
app_config = get_app_config()

def get_llm(model_name=None, temperature=None, base_url=None):
    """Get the Ollama language model.
    
    Args:
        model_name: Name of the Ollama model to use (overrides config)
        temperature: Temperature for text generation (overrides config)
        base_url: URL of the Ollama server (overrides config)
        
    Returns:
        An initialized OllamaLLM instance
        
    Raises:
        HTTPException: If Ollama server is unavailable
    """
    # Use provided values or defaults from config
    model = model_name or app_config["ollama_model"]
    temp = temperature if temperature is not None else app_config["temperature"]
    url = base_url or app_config["ollama_base_url"]
    
    try:
        logger.info(f"Initializing Ollama LLM with model: {model}")
        return OllamaLLM(
            model=model,
            temperature=temp,
            base_url=url
            # stop=["\n\n"]
        )
    except Exception as e:
        logger.error(f"Error initializing Ollama: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service is unavailable. Make sure Ollama is running at {url}"
        )
