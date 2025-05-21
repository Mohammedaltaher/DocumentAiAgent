@echo off
echo Clearing ChromaDB collections...
cd %~dp0
python clear_chromadb.py
echo Done. ChromaDB has been cleared.
pause
