"""
Arabic text handling test script.
This script tests the Arabic language detection and text formatting.
"""
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.language import detect_language, format_text_for_direction

def run_tests():
    """Run test cases for Arabic language detection and formatting."""
    test_cases = [
        "Hello world",
        "مرحبا بالعالم",
        "Hello with بعض الكلمات العربية",
        "1234567890",
        "١٢٣٤٥٦٧٨٩٠",  # Arabic numerals
        "",  # Empty string
    ]
    
    print("=== Testing Arabic language detection and formatting ===")
    for i, text in enumerate(test_cases):
        detected = detect_language(text)
        formatted = format_text_for_direction(text, detected)
        
        print(f"\nTest case {i+1}:")
        print(f"Text: {text}")
        print(f"Detected language: {detected}")
        print(f"Formatted text: {formatted}")
        print(f"Contains invisible RTL/LTR mark: {'Yes' if len(formatted) > len(text) else 'No'}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    run_tests()
