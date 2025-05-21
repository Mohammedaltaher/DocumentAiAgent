"""
API routes for document upload and management.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from app.core.document_store import DocumentStore

# Set up logging
logger = logging.getLogger(__name__)

# Initialize document store
document_store = DocumentStore()

# Create router
router = APIRouter(tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the system.
    
    Args:
        file: The file to upload (PDF or TXT)
        
    Returns:
        document_id: The ID of the uploaded document
    """
    # Get file content
    content = await file.read()
    
    # Get file extension
    filename = file.filename or "unknown_file"
    file_extension = filename.split(".")[-1].lower() if filename and "." in filename else ""
    
    if file_extension not in ["pdf", "txt"]:
        logger.warning(f"Unsupported file type: {file_extension}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )
    
    try:
        # Add document to store
        document_id = await document_store.add_document(
            file_content=content,
            file_name=filename,
            file_type=file_extension
        )
        
        logger.info(f"Document uploaded successfully: {filename} (id: {document_id})")
        return {"document_id": document_id, "filename": filename}
    
    except Exception as e:
        logger.error(f"Failed to process document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    try:
        documents = document_store.list_documents()
        logger.info(f"Retrieved list of {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.get("/documents/stats")
async def get_document_stats():
    """
    Get statistics about the document store.
    
    Returns:
        document_count: Number of documents in the store
        storage_size: Estimated size of the document store in bytes
    """
    try:
        # Get document metadata dictionary
        documents_metadata = document_store.list_documents()
        
        # Calculate total size (this is an estimate based on stored metadata)
        total_size = 0
        for doc_id, doc_meta in documents_metadata.items():
            # Use file_size field if available, otherwise estimate based on chunk count
            if 'file_size' in doc_meta:
                total_size += doc_meta['file_size']
            elif 'chunk_count' in doc_meta:
                # Estimate ~1KB per chunk
                total_size += doc_meta.get('chunk_count', 0) * 1024
        
        stats = {
            "document_count": len(documents_metadata),
            "storage_size": total_size
        }
        
        logger.info(f"Retrieved document store stats: {len(documents_metadata)} documents")
        return stats
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting document stats: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the system.
    
    Args:
        document_id: The ID of the document to delete
        
    Returns:
        success: Whether the document was successfully deleted
    """
    try:
        success = document_store.delete_document(document_id)
        if success:
            logger.info(f"Document deleted successfully: {document_id}")
            return {"success": True, "document_id": document_id}
        else:
            logger.warning(f"Document not found: {document_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {document_id}"
            )
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )
