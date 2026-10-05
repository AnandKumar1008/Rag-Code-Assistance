import os
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Use Qdrant in local file mode (no Docker/server needed!)
QDRANT_PATH = "/data1/anandkumar/qdrant_local"

# Initialize Ollama Embeddings on private port
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:23456")

# Initialize Qdrant Client in local file mode
try:
    client = QdrantClient(path=QDRANT_PATH)
    print(f"Qdrant local mode initialized at {QDRANT_PATH}")
except Exception as e:
    print(f"Warning: Could not initialize Qdrant: {e}")
    client = None

COLLECTION_NAME = "research_papers"
VECTOR_SIZE = 768  # nomic-embed-text output dimension

from typing import List

def _ensure_collection_exists():
    """Create the collection if it doesn't exist yet."""
    if client is None:
        return
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        print(f"Created collection '{COLLECTION_NAME}'")

def get_vector_store():
    """Helper to get the vector store instance."""
    if client is None:
        return None
    _ensure_collection_exists()
    return Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings
    )

def index_documents(docs: List[Document]):
    vectorstore = get_vector_store()
    if vectorstore is None:
        print("Qdrant is not available. Skipping indexing.")
        return
    vectorstore.add_documents(docs)
    print(f"Indexed {len(docs)} documents.")

def retrieve_chunks(query: str, k: int = 5):
    vectorstore = get_vector_store()
    if vectorstore is None:
        print("Qdrant is not available. Returning empty results.")
        return []
    try:
        return vectorstore.similarity_search(query, k=k)
    except Exception as e:
        print(f"Retrieval failed: {e}")
        return []
