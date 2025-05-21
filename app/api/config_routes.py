"""
API routes for configuration management.
"""
import os
import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.utils.config import get_app_config
from app.utils.env import get_settings, find_settings_file
from app.core.ollama_models import get_ollama_models
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConfigSettings(BaseModel):
    """Configuration settings model."""
    ollama_base_url: str
    ollama_model: str
    temperature: float
    chroma_persist_dir: str
    max_context: int
    default_language: Optional[str] = "auto"

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    model: str

class ModelsResponse(BaseModel):
    """Models list response model."""
    models: List[str]

def read_settings_file():
    """Read the settings.json file contents into a dictionary."""
    settings = get_settings()
    if not settings:
        # Return default settings if file doesn't exist
        return {
            "ollama_base_url": "http://192.168.21.237:11434/",
            "ollama_model": "deepseek-r1:8b",
            "temperature": 0.1,
            "chroma_persist_dir": "./chroma_db",
            "max_context": 120,
            "default_language": "auto"
        }
    return settings

def write_settings_file(settings):
    """Write settings to settings.json file."""
    settings_path = find_settings_file()
    if not settings_path:
        settings_path = "settings.json"
    
    # Write to file
    with open(settings_path, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)

@router.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration settings."""
    try:
        config = read_settings_file()
        return config
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting configuration: {str(e)}")

@router.post("/config", response_model=Dict[str, str])
async def update_config(config: ConfigSettings):
    """Update configuration settings."""
    try:
        # Convert to dictionary for easier handling
        config_dict = config.dict()
        
        # Update environment variables for the current session
        for key, value in config_dict.items():
            os.environ[key.upper()] = str(value)
        
        # Write updated settings to file
        write_settings_file(config_dict)
        
        return {"status": "success", "message": "Configuration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health of the service."""
    try:
        config = read_settings_file()
        return {
            "status": "ok",
            "model": config["ollama_model"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """Get list of available models from Ollama server."""
    try:
        config = read_settings_file()
        base_url = config.get("ollama_base_url", "http://localhost:11434/")
        models = get_ollama_models(base_url)
        return {"models": models}
    except Exception as e:
        logger.error(f"Error fetching models from Ollama: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching models from Ollama: {str(e)}")
