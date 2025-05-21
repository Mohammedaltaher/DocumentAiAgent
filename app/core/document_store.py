"""
Document storage and retrieval module.
This module handles storing, processing, and retrieving documents using vector embeddings.
"""
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import uuid
import tempfile
import logging
import json
from typing import Dict, List, Optional

from app.utils.config import get_app_config

# Set up logging
logger = logging.getLogger(__name__)

# Get application configuration
app_config = get_app_config()

class DocumentStore:
    def __init__(self, persist_directory=None):
        """Initialize the document store with a ChromaDB backend.
        
        Args:
            persist_directory: Directory where ChromaDB will store its data
        """
        self.persist_directory = persist_directory or app_config["chroma_persist_dir"]
        # Use a good local embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Create the persistent ChromaDB instance
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        # Keep track of document metadata
        self.documents_metadata: Dict[str, dict] = {}
        self.metadata_file = os.path.join(self.persist_directory, "metadata.json")
        
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Load existing metadata if available
        self._load_metadata()
        
        logger.info(f"Document store initialized with persist directory: {self.persist_directory}")
    
    def _save_metadata(self):
        """Save document metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.documents_metadata, f)
            logger.info(f"Saved metadata for {len(self.documents_metadata)} documents")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
    
    def _load_metadata(self):
        """Load document metadata from disk if available."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.documents_metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.documents_metadata)} documents")
            except Exception as e:
                logger.error(f"Error loading metadata: {str(e)}")
                self.documents_metadata = {}
        else:
            logger.info("No metadata file found, starting with empty metadata")
            self.documents_metadata = {}
    
    def _get_loader(self, file_path: str, file_type: str):
        """Get the appropriate document loader based on file type.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the file (pdf, txt, etc.)
            
        Returns:
            A document loader for the specified file type
            
        Raises:
            ValueError: If file type is not supported
        """
        if file_type.lower() == "pdf":
            return PyPDFLoader(file_path)
        elif file_type.lower() in ["txt", "text"]:
            return TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _process_documents(self, documents):
        """Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of document chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(documents)
    
    async def add_document(self, file_content: bytes, file_name: str, file_type: str) -> str:
        """
        Add a document to the store and return its ID.
        
        Args:
            file_content: The binary content of the file
            file_name: Original filename
            file_type: Type of the file (pdf, txt, etc.)
            
        Returns:
            document_id: Unique ID for the uploaded document
            
        Raises:
            ValueError: If file type is not supported
            Exception: For document processing errors
        """
        # Generate a unique ID for this document
        document_id = str(uuid.uuid4())
        
        logger.info(f"Adding document: {file_name} (type: {file_type}, id: {document_id})")
        
        # Create a temporary file to pass to the document loader
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Load the document
            loader = self._get_loader(temp_file_path, file_type)
            documents = loader.load()
            
            # Add document metadata
            for doc in documents:
                doc.metadata["document_id"] = document_id
                doc.metadata["file_name"] = file_name

            # Process the documents (split into chunks)
            chunks = self._process_documents(documents)
            
            logger.info(f"Document {document_id} split into {len(chunks)} chunks")
            
            # Add to ChromaDB
            self.db.add_documents(chunks)
            
            # Store metadata
            self.documents_metadata[document_id] = {
                "file_name": file_name,
                "file_type": file_type,
                "chunk_count": len(chunks)
            }
            
            # Save metadata to disk
            self._save_metadata()
            
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document {file_name}: {str(e)}")
            raise
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def get_retriever(self, document_ids: Optional[List[str]] = None):
        """
        Get a retriever for the specified documents or all documents.
        
        Args:
            document_ids: List of document IDs to retrieve from, or None for all documents
            
        Returns:
            A configured retriever
        """        # If specific document IDs are provided, filter for those
        if document_ids:
            logger.info(f"Creating retriever for specific documents: {document_ids}")
            retriever = self.db.as_retriever(
                search_kwargs={
                    "filter": {"document_id": {"$in": document_ids}},
                    "k": app_config["max_context"]
                }
            )
        else:
            # Otherwise return a retriever for all documents
            logger.info("Creating retriever for all documents")
            retriever = self.db.as_retriever(
                search_kwargs={"k": app_config["max_context"]}
            )
            
        return retriever
    
    def list_documents(self):
        """Return a list of stored documents with their metadata."""
        return self.documents_metadata
        
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            document_id: The ID of the document to delete
            
        Returns:
            bool: True if the document was deleted, False otherwise
        """
        if document_id not in self.documents_metadata:
            logger.warning(f"Attempted to delete non-existent document: {document_id}")
            return False
            
        try:
            # Delete from ChromaDB
            self.db.delete(where={"document_id": document_id})
            
            # Remove from metadata
            del self.documents_metadata[document_id]
            
            # Save updated metadata
            self._save_metadata()
            
            logger.info(f"Document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
