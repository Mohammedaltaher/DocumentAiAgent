"""
Tests for document_store module.
"""
import pytest
import tempfile
import os
from app.core.document_store import DocumentStore

@pytest.fixture
def document_store():
    """Create a temporary document store for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield DocumentStore(persist_directory=temp_dir)

def test_document_store_initialization(document_store):
    """Test that the document store initializes correctly."""
    assert document_store is not None
    assert document_store.db is not None
    
# Add more tests for document_store methods
