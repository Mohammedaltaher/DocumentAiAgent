import chromadb
import os
import sys

# Get the parent directory (project root)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Initialize ChromaDB client
client = chromadb.PersistentClient(os.path.join(parent_dir, "chroma_db"))

# List all collections
collections = client.list_collections()
print(f"Found {len(collections)} collections")

for collection in collections:
    collection_name = collection.name
    print(f"Deleting collection: {collection_name}")
    client.delete_collection(collection_name)

print("All collections have been deleted successfully.")
