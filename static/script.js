// Global variables
let apiUrl = 'http://localhost:8000/api';  // Make sure this matches your FastAPI server address
let conversationId = null;
let documents = {};

// Simple HTML sanitizer to prevent XSS attacks while preserving basic formatting
function sanitizeHTML(html) {
    const temp = document.createElement('div');
    temp.textContent = html;
    
    // Convert markdown-like syntax to HTML
    let sanitized = temp.innerHTML;
    
    // Convert **text** to <strong>text</strong> (bold)
    sanitized = sanitized.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert numbered lists (1. item, 2. item, etc.)
    sanitized = sanitized.replace(/^\d+\.\s+(.*?)(?=\n\d+\.|\n\n|$)/gm, '<li>$1</li>');
    
    // Convert bulleted lists (- item, * item)
    sanitized = sanitized.replace(/^[-*]\s+(.*?)(?=\n[-*]|\n\n|$)/gm, '<li>$1</li>');
    
    // Wrap adjacent list items in <ul> or <ol>
    sanitized = sanitized.replace(/<li>(.*?)(?=<li>|$)/g, '<ul><li>$1</ul>');
    
    // Convert --- to horizontal rule
    sanitized = sanitized.replace(/---/g, '<hr>');
    
    // Convert ### Heading to <h3>Heading</h3>
    sanitized = sanitized.replace(/###\s+(.*?)(?=\n|$)/g, '<h3>$1</h3>');
    
    // Convert code blocks with ```
    sanitized = sanitized.replace(/```([\s\S]*?)```/g, '<div class="code-block">$1</div>');
    
    // Convert > quotes to blockquote
    sanitized = sanitized.replace(/^>\s+(.*?)(?=\n[^>]|\n\n|$)/gm, '<blockquote>$1</blockquote>');
    
    return sanitized;
}

// DOM elements
const uploadForm = document.getElementById('upload-form');
const documentFile = document.getElementById('document-file');
const uploadStatus = document.getElementById('upload-status');
const documentsContainer = document.getElementById('documents-container');
const chatMessages = document.getElementById('chat-messages');
const questionInput = document.getElementById('question-input');
const askButton = document.getElementById('ask-button');


// Fetch documents on page load
window.addEventListener('DOMContentLoaded', () => {
    fetchDocuments();
});

// Handle document upload
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!documentFile.files.length) {
        alert('Please select a file to upload');
        return;
    }
    
    const file = documentFile.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    uploadStatus.textContent = 'Uploading...';
    
    try {
        const response = await fetch(`${apiUrl}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        uploadStatus.textContent = 'Upload successful!';
        documentFile.value = '';
        
        // Refresh document list
        fetchDocuments();
        
    } catch (error) {
        uploadStatus.textContent = `Error: ${error.message}`;
    }
});

// Fetch all documents
async function fetchDocuments() {
    try {
        const response = await fetch(`${apiUrl}/documents`);
        if (!response.ok) {
            throw new Error(`Failed to fetch documents: ${response.statusText}`);
        }
        
        documents = await response.json();
        
        if (Object.keys(documents).length === 0) {
            documentsContainer.innerHTML = '<p>No documents uploaded yet.</p>';
            questionInput.disabled = true;
            askButton.disabled = true;
            return;
        }
        
        // Enable chat if documents exist
        questionInput.disabled = false;
        askButton.disabled = false;
        
        // Display documents
        renderDocuments();
        
    } catch (error) {
        documentsContainer.innerHTML = `<p>Error loading documents: ${error.message}</p>`;
    }
}

// Render document list
function renderDocuments() {
    let html = '';
    
    for (const [id, metadata] of Object.entries(documents)) {
        html += `
            <div class="document-item" data-id="${id}">
                <label>
                    <button class="delete-btn" data-id="${id}"><i class="fas fa-times"></i></button>
                    <input type="checkbox" class="document-checkbox" data-id="${id}" checked>
                    ${metadata.file_name}
                </label>
            </div>
        `;
    }
    
    documentsContainer.innerHTML = html;
    
    // Add event listeners to delete buttons
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', handleDeleteDocument);
    });
}

// Handle document deletion
async function handleDeleteDocument(e) {
    e.stopPropagation(); // Prevent event bubbling
    
    // Get the ID from either the icon or the button itself
    const button = e.target.closest('.delete-btn');
    const documentId = button.dataset.id;
    const documentName = documents[documentId]?.file_name || 'this document';
    
    if (!confirm(`Are you sure you want to delete ${documentName}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${apiUrl}/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`Delete failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Remove from documents object
            delete documents[documentId];
            
            // Re-render document list
            renderDocuments();
            
            // Show success message
            uploadStatus.textContent = `Document "${documentName}" deleted successfully.`;
            
            // Disable chat if no documents left
            if (Object.keys(documents).length === 0) {
                documentsContainer.innerHTML = '<p>No documents uploaded yet.</p>';
                questionInput.disabled = true;
                askButton.disabled = true;
            }
        }
        
    } catch (error) {
        alert(`Error deleting document: ${error.message}`);
    }
}

// Handle asking questions
askButton.addEventListener('click', async () => {
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    // Get selected document IDs
    const selectedDocuments = [];
    document.querySelectorAll('.document-checkbox:checked').forEach(checkbox => {
        selectedDocuments.push(checkbox.dataset.id);
    });
    
    if (selectedDocuments.length === 0) {
        alert('Please select at least one document');
        return;
    }
    
    // Add user message to chat
    addMessage(question, 'user');
    
    // Clear input
    questionInput.value = '';
    
    // Add loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Thinking...';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
      // Prepare form data
    const formData = new FormData();
    formData.append('question', question);
    selectedDocuments.forEach(id => {
        formData.append('document_ids', id);
    });
    
    // Add conversation ID for context
    if (conversationId) {
        formData.append('conversation_id', conversationId);
    }
    
    
    try {
        const response = await fetch(`${apiUrl}/ask`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get answer: ${response.statusText}`);
        }
        
        // Remove loading message
        chatMessages.removeChild(loadingDiv);
          const result = await response.json();
        
        // Store conversation ID for context
        conversationId = result.conversation_id;
        
        const responseDirection = result.direction || 'ltr';
        
        // Add bot response to chat with correct direction
        addMessage(result.answer, 'bot', result.sources, responseDirection);
        
    } catch (error) {
        // Remove loading message
        chatMessages.removeChild(loadingDiv);
        
        // Add error message
        addMessage(`Error: ${error.message}`, 'bot');
    }
});

// Allow pressing Enter to submit question
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askButton.click();
    }
});

// Detect if text contains RTL characters
function containsRTL(text) {
    const rtlRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    return rtlRegex.test(text);
}

// Apply correct directionality to message
function applyTextDirection(element, text) {
    if (containsRTL(text)) {
        element.classList.add('rtl-text');
    } else {
        element.classList.add('ltr-text');
    }
}

// Add a message to the chat
function addMessage(text, sender, sources = [], direction = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Apply text direction if specified or auto-detect
    if (direction === 'rtl') {
        messageDiv.classList.add('rtl-text');
    } else if (direction === 'ltr') {
        messageDiv.classList.add('ltr-text');
    } else {
        // Auto-detect based on content
        applyTextDirection(messageDiv, text);
    }
      // Check for think tags in the message
    const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
    let hasThinkContent = thinkRegex.test(text);
    let displayText = text;
    let thinkContent = '';
    
    if (hasThinkContent) {
        // Reset regex state after the test above
        thinkRegex.lastIndex = 0;
        
        // Extract thinking content
        const match = thinkRegex.exec(text);
        if (match && match[1]) {
            thinkContent = match[1].trim();
            // Remove the think tags from the display text
            displayText = text.replace(/<think>[\s\S]*?<\/think>/, '').trim();
        }
    }
      // Process the text for markdown-like formatting and sanitize it
    let formattedText = sanitizeHTML(displayText);
    
    // Set the visible content with proper formatting
    messageDiv.innerHTML = formattedText;
    
    // Add thinking content if available
    if (thinkContent) {
        const thinkToggle = document.createElement('div');
        thinkToggle.className = 'thinking-toggle';
        thinkToggle.textContent = 'Show thinking process';
        messageDiv.appendChild(thinkToggle);
          const thinkDiv = document.createElement('div');
        thinkDiv.className = 'thinking-content';
        thinkDiv.innerHTML = sanitizeHTML(thinkContent);
        messageDiv.appendChild(thinkDiv);
        
        // Add toggle functionality
        thinkToggle.addEventListener('click', () => {
            const isVisible = thinkDiv.style.display === 'block';
            thinkDiv.style.display = isVisible ? 'none' : 'block';
            thinkToggle.textContent = isVisible ? 'Show thinking process' : 'Hide thinking process';
        });
    }
      // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'sources';
        
        // Apply same direction as the message
        if (messageDiv.classList.contains('rtl-text')) {
            sourcesDiv.classList.add('rtl-text');
            sourcesDiv.innerHTML = '<strong>المصادر:</strong>';
        } else {
            sourcesDiv.innerHTML = '<strong>Sources:</strong>';
        }

        // Collect unique file names
        const uniqueFileNames = new Set();
        sources.forEach(source => {
            if (source.metadata && source.metadata.file_name) {
                uniqueFileNames.add(source.metadata.file_name);
            }
        });        Array.from(uniqueFileNames).forEach(fileName => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            
            // Format source text based on direction
            if (messageDiv.classList.contains('rtl-text')) {
                sourceItem.textContent = `من ${fileName}`;
                sourceItem.classList.add('rtl-text');
            } else {
                sourceItem.textContent = `From ${fileName}`;
            }
            
            sourcesDiv.appendChild(sourceItem);
        });

        messageDiv.appendChild(sourcesDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
