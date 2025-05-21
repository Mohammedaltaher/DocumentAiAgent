import requests
from typing import List

def get_ollama_models(base_url: str) -> List[str]:
    """Fetches the list of available models from the Ollama server."""
    try:
        response = requests.get(f"{base_url.rstrip('/')}/api/tags")
        response.raise_for_status()
        data = response.json()
        # The models are typically under the 'models' or 'models' key, depending on Ollama's API
        # We'll try both for compatibility
        if 'models' in data:
            return [m['name'] for m in data['models']]
        elif 'tags' in data:
            return [m['name'] for m in data['tags']]
        else:
            return []
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models from Ollama: {e}")
