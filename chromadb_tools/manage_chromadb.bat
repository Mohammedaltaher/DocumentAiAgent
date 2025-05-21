@echo off
echo ChromaDB Management Tools
echo ---------------------
echo 1. View ChromaDB Collections
echo 2. Clear ChromaDB Collections
echo 3. Exit
echo.

choice /C 123 /N /M "Choose an option (1-3): "

if errorlevel 3 goto :end
if errorlevel 2 goto :clear
if errorlevel 1 goto :view

:view
cd chromadb_tools
call run_chromadb_viewer.bat
goto :end

:clear
cd chromadb_tools
call clear_chromadb.bat
goto :end

:end
echo Goodbye!
