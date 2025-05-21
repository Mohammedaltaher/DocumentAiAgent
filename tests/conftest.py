"""
Configuration for pytest.
"""
import pytest
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test-specific fixtures and configuration can be added here
