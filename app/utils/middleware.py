"""
Basic middleware for request logging and error handling.
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and log information about it.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response from the next middleware or endpoint
        """
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = request.url
        client = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"Request: {method} {url} from {client}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"Response: {method} {url} - {response.status_code} ({process_time:.4f}s)")
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(f"Error processing {method} {url}: {str(e)}")
            
            # Re-raise for FastAPI exception handlers
            raise

class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding language-specific headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and add language headers if needed.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint handler
            
        Returns:
            The response with added language headers if needed
        """
        response = await call_next(request)
        
        # Check if this is a QA response by parsing the path
        if request.url.path.startswith("/api/ask"):
            response.headers["X-Text-Direction"] = "auto"
        
        return response
