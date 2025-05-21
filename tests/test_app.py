"""
Basic tests for the Document QA Agent.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create a test client
client = TestClient(app)

def test_api_root():
    """Test the API root endpoint."""
    response = client.get("/api")
    assert response.status_code == 200
    assert response.json() == {"message": "Document QA API is running"}

def test_index_html():
    """Test the index.html endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Document QA Agent" in response.text
    
# Add more tests as needed
