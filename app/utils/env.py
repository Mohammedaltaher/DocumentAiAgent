"""
Settings utility module.
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

def load_env_file(settings_file: Optional[str] = None) -> None:
    """
    Load settings from settings.json file into environment variables.
    
    Args:
        settings_file: Path to the settings.json file. If None, attempts to find a settings.json file
                      in the current directory or parent directories.
    """
    if settings_file and os.path.exists(settings_file):
        # If specific file is provided and exists, load it
        load_settings_to_env(settings_file)
        return
    
    # Try to find settings.json file in current dir or parent dirs
    settings_path = find_settings_file()
    if settings_path:
        load_settings_to_env(settings_path)

def load_settings_to_env(settings_path: str) -> None:
    """
    Load settings from JSON file into environment variables.
    
    Args:
        settings_path: Path to the settings.json file
    """
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        # Convert settings to uppercase environment variables
        for key, value in settings.items():
            os.environ[key.upper()] = str(value)
    except Exception as e:
        print(f"Error loading settings from {settings_path}: {str(e)}")

def find_settings_file() -> Optional[str]:
    """
    Find a settings.json file in the current directory or parent directories.
    
    Returns:
        Path to the settings.json file if found, None otherwise
    """
    current_dir = Path.cwd()
    
    # Check current dir
    settings_path = current_dir / 'settings.json'
    if settings_path.exists():
        return str(settings_path)
    
    # Check parent dirs (up to 3 levels)
    for _ in range(3):
        current_dir = current_dir.parent
        settings_path = current_dir / 'settings.json'
        if settings_path.exists():
            return str(settings_path)
    
    return None

def get_settings() -> Dict[str, Any]:
    """
    Get settings from settings.json file.
    
    Returns:
        Dictionary containing settings
    """
    settings_path = find_settings_file()
    if not settings_path:
        return {}
        
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
