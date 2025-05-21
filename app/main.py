"""
Main module for the Document QA Agent application.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os

from app.api import document_routes, qa_routes, config_routes
from app.utils.config import setup_logging, get_app_config
from app.utils.middleware import LoggingMiddleware, LanguageMiddleware

# Configure logging
setup_logging()

logger = logging.getLogger(__name__)

# Load application configuration
app_config = get_app_config()

# Initialize FastAPI app
app = FastAPI(
    title="Document QA Agent",
    description="An agent that can answer questions based on uploaded documents",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests (for web UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add language middleware
app.add_middleware(LanguageMiddleware)

# Current directory for static files
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(os.path.dirname(current_dir), "static")

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers from api modules
app.include_router(document_routes.router, prefix="/api")
app.include_router(qa_routes.router, prefix="/api")
app.include_router(config_routes.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the index.html file."""
    try:
        index_path = os.path.join(static_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading index.html: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to load application"
        )

@app.get("/api")
async def api_root():
    """API root endpoint to check if API is running."""
    return {"message": "Document QA API is running"}

if __name__ == "__main__":
    # Start the server with uvicorn when script is run directly
    logger.info("Starting Document QA API server")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
