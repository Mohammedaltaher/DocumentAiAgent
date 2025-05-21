# ChromaDB Tools

This folder contains tools for working with ChromaDB in the Customer Support Agent project.

## Available Tools

1. **ChromaDB Viewer** - A Streamlit application to visualize and explore the ChromaDB collections.
   - Run with: `run_chromadb_viewer.bat`

2. **Clear ChromaDB** - A script to delete all collections in ChromaDB.
   - Run with: `clear_chromadb.bat`

## Usage

- To view your ChromaDB collections, simply run the `run_chromadb_viewer.bat` file.
- To clear all collections in your ChromaDB database, run the `clear_chromadb.bat` file.

## Notes

- These tools access the ChromaDB database located in the parent directory at `../chroma_db`.
- Make sure to backup important data before clearing collections if needed.
