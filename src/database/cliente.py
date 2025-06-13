from openai import OpenAI
import os
import chromadb
from chromadb.utils import embedding_functions
from config import settings

class ChromaDBClient:
    def __init__(self, path: str = "chroma_db"):
        """Initialize a persistent ChromaDB client with OpenAI embeddings."""
        self.client = chromadb.PersistentClient(path=path)
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self._get_openai_key(),
            model_name="text-embedding-3-small"
        )
    
    def _get_openai_key(self) -> str:
        """Load OpenAI API key securely."""
        key = settings.openai_api_key
        if not key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return key
    
    def get_collection(self, name: str = "image_audio_data") -> chromadb.Collection:
        """Get or create a collection with the specified name."""
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.openai_ef
        )
    def clear_collection(self, name: str = "image_audio_data") -> bool:
        """
        Completely clears a collection while keeping it available for future use.
        Returns True if successful, False otherwise.
        """
        try:
            self.client.delete_collection(name=name)
            # Recreate the collection to maintain structure
            self.get_collection(name=name)  # Uses your existing get_collection method
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

# Singleton instance (optional but recommended)
db_client = ChromaDBClient()
collection = db_client.get_collection()