"""
Entry point for the Document QA Agent application.
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Set console encoding to UTF-8 for proper display of Arabic text
    # if sys.platform == 'win32':
        # Set Windows console to UTF-8 mode
        # os.system('chcp 65001')
        
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
