"""
Vector Store service for FAISS-based document retrieval.
"""
import os
import pickle
from typing import Optional
import faiss
import numpy as np
from ..config import get_settings
from .embeddings import get_embedding_service


class VectorStoreService:
    """Service for managing FAISS vector store operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.index: Optional[faiss.Index] = None
        self.metadata_store: dict = {}
        self.text_store: dict = {}
        
    def initialize(self) -> bool:
        """
        Load the FAISS index and associated metadata.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            vector_dir = self.settings.vector_store_dir
            
            print("Loading FAISS Index...")
            self.index = faiss.read_index(os.path.join(vector_dir, 'index.faiss'))
            
            with open(os.path.join(vector_dir, 'metadata.pkl'), 'rb') as f:
                self.metadata_store = pickle.load(f)
                
            with open(os.path.join(vector_dir, 'texts.pkl'), 'rb') as f:
                self.text_store = pickle.load(f)
                
            print(f"✅ Vector Store Loaded. Total Vectors: {self.index.ntotal}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load vector store: {e}")
            return False
    
    def search(self, query_text: str, k: Optional[int] = None) -> list[str]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query_text: The search query
            k: Number of results to return (default from settings)
            
        Returns:
            List of formatted document strings with source and content
        """
        if self.index is None:
            return ["[ERROR] Index not loaded"]
            
        k = k or self.settings.retriever_top_k
        embedding_service = get_embedding_service()
        
        vector = embedding_service.encode(query_text)
        D, I = self.index.search(np.array([vector]).astype('float32'), k)
        
        retrieved = []
        for idx in I[0]:
            if idx == -1:
                continue
            meta = self.metadata_store.get(idx, {})
            source = meta.get('source', 'Unknown')
            content = self.text_store.get(idx, '')
            retrieved.append(f"Source: {source}\nContent: {content}")
            
        return retrieved
    
    @property
    def total_vectors(self) -> int:
        """Get the total number of vectors in the index."""
        return self.index.ntotal if self.index else 0


# Singleton instance
_vector_store: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
        _vector_store.initialize()
    return _vector_store
