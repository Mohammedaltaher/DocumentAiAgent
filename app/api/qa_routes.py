"""
API routes for question answering.
"""
from fastapi import APIRouter, Form, HTTPException
from langchain.chains import ConversationalRetrievalChain
from typing import List, Optional, Dict
import logging

from app.core.document_store import DocumentStore
from app.core.llm import get_llm
from app.core.memory_store import get_or_create_memory, get_memory, list_conversation_ids, save_conversations
from app.utils.language import format_text_for_direction , is_arabic_text
from app.utils.config import get_app_config

# Set up logging
logger = logging.getLogger(__name__)

# Initialize document store
document_store = DocumentStore()

# Create router
router = APIRouter(tags=["qa"])

@router.post("/ask")
async def ask_question(
    question: str = Form(...),
    document_ids: Optional[List[str]] = Form(None),
    conversation_id: Optional[str] = Form(None),
):
    """
    Ask a question about the uploaded documents.
    
    Args:
        question: The question to ask
        document_ids: Optional list of specific document IDs to query
        conversation_id: Optional conversation ID for maintaining context
    
    Returns:
        The answer to the question
    """
    logger.info(f"Question received: '{question}'")
    if document_ids:
        logger.info(f"Document IDs specified: {document_ids}")
    if conversation_id:
        logger.info(f"Using conversation ID: {conversation_id}")
    
    try:
        # Initialize or get conversation memory
        memory, conversation_id = get_or_create_memory(conversation_id)
        
        # Get retriever for the specified documents
        retriever = document_store.get_retriever(document_ids)
        
        # Initialize LLM
        llm = get_llm()
        
        # Create conversational chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            return_generated_question=False,
            output_key="answer"  # Specify which output key to use for memory
        )
        
        # Get answer
        logger.info(f"Querying LLM for answer to: '{question}'")
        current_model = get_app_config().get("ollama_model", "").lower()
        logger.info(f"Current model being used: {current_model}")
        
        # Always use single input mode, as system_template is removed
        logger.info(f"Using single input mode (model: {current_model})")
        result = qa_chain.invoke({"question": question})
        
        # Extract answer and sources
        answer = result["answer"]
        
        # Format answer according to language direction
        formatted_answer = format_text_for_direction(answer)
        
        # Save conversations after successful interaction
        save_conversations()
        logger.info(f"Conversation {conversation_id} saved after new interaction.")

        # Extract and format source documents
        sources = []
        for doc in result.get("source_documents", []):
            source = {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source)
        
        logger.info(f"Answer generated with {len(sources)} source references")
        
        # Determine text direction based on the content of the answer
        
        # Check if the formatted answer contains Arabic text
        is_rtl = is_arabic_text(formatted_answer)
        
        return {
            "answer": formatted_answer,
            "sources": sources,
            "conversation_id": conversation_id,
            "direction": "rtl" if is_rtl else "ltr"
        }
        
    except Exception as e:
        logger.error(f"Failed to answer question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(e)}"
        )

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get the chat history for a given conversation ID.
    """
    memory = get_memory(conversation_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Extract chat history from memory
    chat_history = []
    for msg in memory.chat_memory.messages:
        chat_history.append({
            "type": msg.type,
            "content": msg.content
        })
    return {
        "conversation_id": conversation_id,
        "chat_history": chat_history
    }

@router.get("/conversations")
async def list_conversations():
    """
    Get a list of all available conversation IDs.
    """
    return {
        "conversations": list_conversation_ids()
    }
