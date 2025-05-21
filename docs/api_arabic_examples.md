# API Documentation for Arabic Language Support

## Overview

This document provides examples of how to use the Document QA API with Arabic language support.

## API Endpoints

### 1. Ask a Question

**Endpoint**: `POST /api/ask`

**Parameters**:
- `question` (required): The question to ask
- `document_ids` (optional): List of document IDs to search within
- `conversation_id` (optional): ID for maintaining conversation context
- `language` (optional): Language code ("english", "arabic", or "auto")

**Example Request (English)**:
```
POST /api/ask
Content-Type: multipart/form-data

question=What is the return policy?
document_ids=doc123
language=english
```

**Example Request (Arabic)**:
```
POST /api/ask
Content-Type: multipart/form-data

question=ما هي سياسة الإرجاع؟
document_ids=doc123
language=arabic
```

**Example Request (Auto-detection)**:
```
POST /api/ask
Content-Type: multipart/form-data

question=ما هي سياسة الإرجاع؟
document_ids=doc123
language=auto
```

**Example Response (Arabic)**:
```json
{
  "answer": "‏وفقًا للمستندات المقدمة، سياسة الإرجاع تسمح بإرجاع المنتجات خلال 30 يومًا من تاريخ الشراء مع وجود إيصال. يجب أن تكون المنتجات في حالتها الأصلية غير المستعملة مع جميع العلامات والتغليف.",
  "sources": [
    {
      "content": "سياسة الإرجاع: يمكن إرجاع المنتجات خلال 30 يومًا من الشراء مع إيصال. يجب أن تكون المنتجات غير مستخدمة وفي حالتها الأصلية مع جميع العلامات والتغليف.",
      "metadata": {
        "file_name": "return_policy.txt",
        "page": 1
      }
    }
  ],
  "conversation_id": "b8a7d3e1-5f2c-4d9e-9b6a-c8e5f3d2a1b0",
  "language": "arabic",
  "direction": "rtl"
}
```

### 2. Get Supported Languages

**Endpoint**: `GET /api/languages`

**Example Response**:
```json
{
  "languages": [
    {"code": "english", "name": "English", "direction": "ltr"},
    {"code": "arabic", "name": "العربية", "direction": "rtl"},
    {"code": "auto", "name": "Auto Detect", "direction": "auto"}
  ]
}
```

### 3. Get Conversation History

**Endpoint**: `GET /api/conversation/{conversation_id}`

**Example Response (Mixed Languages)**:
```json
{
  "conversation_id": "b8a7d3e1-5f2c-4d9e-9b6a-c8e5f3d2a1b0",
  "chat_history": [
    {
      "type": "human",
      "content": "What is the return policy?"
    },
    {
      "type": "ai",
      "content": "According to the provided documents, you can return products within 30 days of purchase with a receipt. Products must be unused and in their original condition with all tags and packaging."
    },
    {
      "type": "human",
      "content": "ما هي سياسة الإرجاع؟"
    },
    {
      "type": "ai",
      "content": "‏وفقًا للمستندات المقدمة، سياسة الإرجاع تسمح بإرجاع المنتجات خلال 30 يومًا من تاريخ الشراء مع وجود إيصال. يجب أن تكون المنتجات في حالتها الأصلية غير المستعملة مع جميع العلامات والتغليف."
    }
  ]
}
```

## Client-Side Handling

When receiving responses with Arabic content:

1. Check the `direction` field in responses (will be "rtl" for Arabic)
2. Apply appropriate CSS styling to display RTL text correctly:
   ```css
   .rtl-text {
       direction: rtl;
       text-align: right;
       font-family: 'Poppins', 'Scheherazade New', sans-serif;
   }
   ```
3. The invisible RTL mark (U+200F) is added automatically to Arabic text

## Best Practices

1. Always set the correct `Content-Type` header
2. Use `language=auto` when you want the system to auto-detect language
3. Handle both LTR and RTL text properly in your UI
4. Use UTF-8 encoding for all communications
