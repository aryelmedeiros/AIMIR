from openai import OpenAI
import os
import chromadb
from chromadb.utils import embedding_functions
from config import settings

class ChromaDBClient:
    def __init__(self, path: str = "chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self._get_openai_key(),
            model_name="text-embedding-3-small"
        )
    
    def _get_openai_key(self) -> str:
        key = settings.openai_api_key
        if not key:
            raise ValueError("OPENAI_API_KEY não encontrada")
        return key
    
    def get_collection(self, name: str = "image_audio_data") -> chromadb.Collection:
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.openai_ef
        )
    def clear_collection(self, name: str = "image_audio_data") -> bool:
        try:
            self.client.delete_collection(name=name)
            # Recriar colecao 
            self.get_collection(name=name) 
            return True
        except Exception as e:
            print(f"Erro ao deletar coleção: {e}")
            return False

db_client = ChromaDBClient()
collection = db_client.get_collection()