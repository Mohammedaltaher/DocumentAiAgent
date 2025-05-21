import streamlit as st
import chromadb
import os
import pandas as pd
import json
from typing import Dict, List, Any

# Set page config
st.set_page_config(
    page_title="ChromaDB Viewer",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 ChromaDB Viewer")
st.markdown("""
This tool allows you to visualize and explore the contents of your ChromaDB vector database.
""")

# Path to ChromaDB
chroma_path = "../chroma_db"

@st.cache_resource
def get_client():
    """Initialize and return a ChromaDB client."""
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        return client
    except Exception as e:
        st.error(f"Error connecting to ChromaDB: {str(e)}")
        return None

def display_collections(client):
    """Display all collections in the database."""
    try:
        collections = client.list_collections()
        if not collections:
            st.warning("No collections found in the database.")
            return None
        
        collection_names = [collection.name for collection in collections]
        selected_collection_name = st.selectbox("Select a collection", collection_names)
        
        if selected_collection_name:
            return client.get_collection(selected_collection_name)
        
        return None
    except Exception as e:
        st.error(f"Error listing collections: {str(e)}")
        return None

def display_collection_details(collection):
    """Display detailed information about a collection."""
    try:
        # Get collection metadata
        count = collection.count()
        st.subheader(f"Collection: {collection.name}")
        st.write(f"Total documents: {count}")
        
        # Get collection data (limited to 100 to prevent UI overload)
        limit = min(100, count)
        if limit == 0:
            st.warning("Collection is empty.")
            return
        
        result = collection.get(limit=limit)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Documents", "Metadata", "Embeddings"])
        
        with tab1:
            if "documents" in result and result["documents"]:
                documents_df = pd.DataFrame({
                    "ID": result["ids"],
                    "Content": result["documents"]
                })
                st.dataframe(documents_df, use_container_width=True)
            else:
                st.warning("No document content found in this collection.")
        
        with tab2:
            if "metadatas" in result and result["metadatas"]:
                # Convert metadata dictionaries to strings for display
                metadata_strings = []
                for metadata in result["metadatas"]:
                    if metadata:
                        metadata_strings.append(json.dumps(metadata, indent=2))
                    else:
                        metadata_strings.append("No metadata")
                
                metadata_df = pd.DataFrame({
                    "ID": result["ids"],
                    "Metadata": metadata_strings
                })
                st.dataframe(metadata_df, use_container_width=True)
            else:
                st.warning("No metadata found in this collection.")
        
        with tab3:
            if "embeddings" in result and result["embeddings"]:
                # Just show dimensions of embeddings
                embed_dim = len(result["embeddings"][0])
                st.write(f"Embedding dimensions: {embed_dim}")
                
                # Create a simplified view of embeddings (first few values)
                embeddings_preview = []
                for i, embedding in enumerate(result["embeddings"]):
                    if i >= 10:  # Limit to first 10 embeddings
                        break
                    preview = str(embedding[:5]) + "... [truncated]"
                    embeddings_preview.append(preview)
                
                embed_df = pd.DataFrame({
                    "ID": result["ids"][:len(embeddings_preview)],
                    "Embedding (preview)": embeddings_preview
                })
                st.dataframe(embed_df, use_container_width=True)
            else:
                st.warning("No embeddings found in this collection.")
    
    except Exception as e:
        st.error(f"Error displaying collection details: {str(e)}")

def search_collection(collection):
    """Allow users to search the collection."""
    if not collection:
        return
    
    st.subheader("Search Collection")
    query = st.text_input("Enter search query")
    n_results = st.slider("Number of results", min_value=1, max_value=20, value=5)
    
    if st.button("Search") and query:
        try:
            # Perform the search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["ids"][0]:
                st.warning("No results found.")
                return
            
            # Display results
            st.subheader("Search Results")
            
            # Create DataFrame for results
            results_data = {
                "ID": results["ids"][0],
                "Document": results["documents"][0],
                "Distance": results["distances"][0]
            }
            
            # Add metadata if available
            if "metadatas" in results and results["metadatas"][0]:
                metadata_str = []
                for metadata in results["metadatas"][0]:
                    metadata_str.append(json.dumps(metadata, indent=2))
                results_data["Metadata"] = metadata_str
            
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error searching collection: {str(e)}")

def main():
    """Main function to run the Streamlit app."""
    # Initialize client
    client = get_client()
    if not client:
        return
    
    # Side by side layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Database Information")
        # Display basic database info
        try:
            collections = client.list_collections()
            st.write(f"Total collections: {len(collections)}")
            st.write("Collections:")
            for collection in collections:
                st.write(f"- {collection.name} ({collection.count()} documents)")
        except Exception as e:
            st.error(f"Error getting database info: {str(e)}")
    
    with col2:
        # Display collections and allow user to select one
        collection = display_collections(client)
        if collection:
            # Display collection details
            display_collection_details(collection)
            
            # Add search functionality
            search_collection(collection)

if __name__ == "__main__":
    main()
