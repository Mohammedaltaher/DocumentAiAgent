# Arabic Language Support - دعم اللغة العربية

This document describes how the Customer Support Agent supports Arabic language for questions and answers.

## Features

- **Auto-detection of Arabic text**: The system automatically detects when questions are asked in Arabic
- **RTL (Right-to-Left) formatting**: Arabic text is displayed with proper RTL formatting
- **Bilingual system prompts**: The LLM is configured with Arabic-specific system prompts
- **Culturally appropriate responses**: The system is designed to provide culturally sensitive responses in Arabic

## Implementation Details

### Language Detection

The system uses character set detection to determine if text contains Arabic characters. If a threshold of Arabic characters is detected, the system will automatically use Arabic mode.

```python
def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    
    Args:
        text: Input text to detect language
        
    Returns:
        Language code (e.g., "english", "arabic")
    """
    # Arabic character ranges
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F')
    
    # If more than 20% of the characters are Arabic, consider it Arabic
    if arabic_chars > len(text) * 0.2:
        return "arabic"
    
    return "english"  # Default to English
```

### RTL Text Formatting

Text direction is automatically set based on the detected language:

```python
def format_text_for_direction(text: str, language_code: str) -> str:
    """
    Format text according to its language direction.
    
    Args:
        text: The text to format
        language_code: The language code (e.g., "english", "arabic")
        
    Returns:
        Formatted text with appropriate direction marks
    """
    direction = get_language_direction(language_code)
    
    if direction == "rtl":
        return f"{RTL_MARK}{text}"
    else:
        return f"{LTR_MARK}{text}"
```

## Language-Specific System Prompts

The LLM uses different system prompts based on the detected language:

```python
# For Arabic:
"""أنت مساعد لخدمة العملاء يستخدم العربية للإجابة على الأسئلة. 
عندما تُسأل سؤالاً باللغة العربية، أجب بالعربية الفصحى. 
استخدم المستندات المقدمة للإجابة على السؤال.
إذا لم تجد الإجابة في المستندات، فقط قل "آسف، لا أستطيع العثور على إجابة لهذا السؤال في المستندات المتاحة."
كن مهذباً ومحترفاً في إجاباتك."""
```

## API Endpoints

A specific endpoint is available to retrieve supported languages:

```
GET /api/languages
```

Sample response:
```json
{
  "languages": [
    {"code": "english", "name": "English", "direction": "ltr"},
    {"code": "arabic", "name": "العربية", "direction": "rtl"},
    {"code": "auto", "name": "Auto Detect", "direction": "auto"}
  ]
}
```

## Usage

To use Arabic language support:

1. **Auto-detection**: Simply type questions in Arabic, and the system will respond in Arabic
2. **Language selection**: Use the language dropdown in the UI to explicitly select Arabic
3. **API usage**: When using the API directly, set the `language` parameter to `"arabic"` 

Example API call with Arabic specified:
```
POST /api/ask
form-data:
  - question: "ما هي سياسة الإرجاع؟"
  - language: "arabic"
  - document_ids: ["doc123"]
```

## Future Improvements

Planned improvements for Arabic language support:

1. Improved document processing for Arabic PDFs
2. Better handling of Arabic dialects beyond Modern Standard Arabic
3. Support for mixed Arabic-English content
4. Enhanced RTL UI components

---

*Document last updated: May 20, 2025*
