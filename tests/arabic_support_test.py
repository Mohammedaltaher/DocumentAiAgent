"""
Arabic Support Testing Script

This script tests the Arabic language support in the Customer Support Agent
by making API calls with Arabic text and verifying the responses.
"""
import requests
import json
import sys
import os
import time

# Constants
API_URL = "http://localhost:8000/api"
TEST_ARABIC_QUESTION = "مرحبا، كيف يمكنني استخدام هذا التطبيق؟"
TEST_ENGLISH_QUESTION = "Hello, how can I use this application?"
TEST_DOCUMENT_CONTENT = """
# نظرة عامة على التطبيق

هذا التطبيق يسمح لك بطرح الأسئلة حول المستندات المرفوعة.
يمكنك رفع ملفات PDF و TXT والبحث فيها.

لاستخدام التطبيق:
1. قم برفع المستندات الخاصة بك
2. اختر المستندات التي ترغب في البحث فيها
3. اكتب سؤالاً واضغط على زر "اسأل"
4. سيقوم النظام بالبحث عن الإجابة في المستندات المحددة

تتوفر هذه الخدمة باللغة العربية والإنجليزية.
"""

def setup_test_document():
    """Create and upload a test document with Arabic content"""
    print("Setting up test document with Arabic content...")
    
    # Create temporary test file
    with open("arabic_test_doc.txt", "w", encoding="utf-8") as f:
        f.write(TEST_DOCUMENT_CONTENT)
    
    # Upload the document
    try:
        files = {"file": open("arabic_test_doc.txt", "rb")}
        response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            doc_id = response.json().get("document_id")
            print(f"Test document uploaded successfully with ID: {doc_id}")
            return doc_id
        else:
            print(f"Failed to upload test document: {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading test document: {str(e)}")
        return None
    finally:
        # Clean up the temporary file
        try:
            os.remove("arabic_test_doc.txt")
        except:
            pass

def test_language_detection():
    """Test the language detection API functionality"""
    print("\nTesting language auto-detection...")
    
    document_id = setup_test_document()
    if not document_id:
        print("Cannot proceed with tests without a test document")
        return False
    
    # Test with Arabic question
    print("\n1. Testing with Arabic question...")
    arabic_data = {
        "question": TEST_ARABIC_QUESTION,
        "document_ids": [document_id],
        "language": "auto"
    }
    
    try:
        response = requests.post(f"{API_URL}/ask", data=arabic_data)
        if response.status_code == 200:
            result = response.json()
            detected_language = result.get("language")
            direction = result.get("direction")
            
            print(f"- Question: {TEST_ARABIC_QUESTION}")
            print(f"- Detected language: {detected_language}")
            print(f"- Text direction: {direction}")
            print(f"- Answer snippet: {result.get('answer')[:100]}...")
            
            if detected_language == "arabic" and direction == "rtl":
                print("✅ Test passed: Arabic was correctly detected")
            else:
                print("❌ Test failed: Arabic was not correctly detected")
                return False
        else:
            print(f"❌ Request failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during Arabic test: {str(e)}")
        return False
    
    # Test with English question
    print("\n2. Testing with English question...")
    english_data = {
        "question": TEST_ENGLISH_QUESTION,
        "document_ids": [document_id],
        "language": "auto"
    }
    
    try:
        response = requests.post(f"{API_URL}/ask", data=english_data)
        if response.status_code == 200:
            result = response.json()
            detected_language = result.get("language")
            direction = result.get("direction")
            
            print(f"- Question: {TEST_ENGLISH_QUESTION}")
            print(f"- Detected language: {detected_language}")
            print(f"- Text direction: {direction}")
            print(f"- Answer snippet: {result.get('answer')[:100]}...")
            
            if detected_language == "english" and direction == "ltr":
                print("✅ Test passed: English was correctly detected")
            else:
                print("❌ Test failed: English was not correctly detected")
                return False
        else:
            print(f"❌ Request failed with status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during English test: {str(e)}")
        return False
    
    return True

def test_arabic_conversation():
    """Test Arabic conversation with context"""
    print("\nTesting Arabic conversation with context...")
    
    document_id = setup_test_document()
    if not document_id:
        print("Cannot proceed with tests without a test document")
        return False
    
    # First question in Arabic
    print("\n1. First question in Arabic...")
    first_data = {
        "question": "ما هي ميزات هذا التطبيق؟",
        "document_ids": [document_id],
        "language": "arabic"
    }
    
    try:
        response = requests.post(f"{API_URL}/ask", data=first_data)
        if response.status_code == 200:
            result = response.json()
            conversation_id = result.get("conversation_id")
            print(f"- Question: {first_data['question']}")
            print(f"- Conversation ID: {conversation_id}")
            print(f"- Answer snippet: {result.get('answer')[:100]}...")
            
            # Second follow-up question
            print("\n2. Follow-up question in Arabic...")
            followup_data = {
                "question": "كيف يمكنني استخدامه؟",
                "document_ids": [document_id],
                "conversation_id": conversation_id,
                "language": "arabic"
            }
            
            response = requests.post(f"{API_URL}/ask", data=followup_data)
            if response.status_code == 200:
                result = response.json()
                print(f"- Question: {followup_data['question']}")
                print(f"- Answer snippet: {result.get('answer')[:100]}...")
                print("✅ Conversation test passed")
                return True
            else:
                print(f"❌ Follow-up request failed: {response.text}")
                return False
        else:
            print(f"❌ Initial request failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during conversation test: {str(e)}")
        return False

def main():
    """Run all Arabic support tests"""
    print("=" * 60)
    print("Arabic Language Support Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}")
        if response.status_code != 200:
            print("Server is not responding. Please make sure the application is running.")
            return
    except:
        print("Cannot connect to the server. Please make sure the application is running at http://localhost:8000/")
        return
    
    # Test language detection
    lang_detection_passed = test_language_detection()
    
    # Test conversation if language detection passed
    if lang_detection_passed:
        conversation_passed = test_arabic_conversation()
    else:
        conversation_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Language Detection: {'✅ Passed' if lang_detection_passed else '❌ Failed'}")
    print(f"Arabic Conversation: {'✅ Passed' if conversation_passed else '❌ Failed'}")
    print("=" * 60)
    
    if lang_detection_passed and conversation_passed:
        print("\n✅ All tests passed! Arabic support is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs above for details.")

if __name__ == "__main__":
    main()
