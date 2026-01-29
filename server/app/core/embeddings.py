"""
Embedding service for text vectorization using Sentence Transformers.
"""
import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ..config import get_settings


class EmbeddingService:
    """Service for generating and comparing text embeddings."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model: Optional[SentenceTransformer] = None
        self.domain_embedding: Optional[np.ndarray] = None
        
    def initialize(self) -> bool:
        """
        Load the embedding model and compute domain embedding.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Loading Embedding Model: {self.settings.embedding_model_name}...")
            self.model = SentenceTransformer(self.settings.embedding_model_name)
            self.domain_embedding = self.model.encode(self.settings.domain_text)
            print("✅ Embedding Model Loaded.")
            return True
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            return False
    
    def encode(self, text: str) -> np.ndarray:
        """Encode text to vector embedding."""
        if self.model is None:
            raise RuntimeError("Embedding model not initialized")
        return self.model.encode(text)
    
    def get_domain_relevance(self, query_text: str) -> float:
        """
        Calculate semantic similarity between query and medical domain.
        
        Args:
            query_text: The user's query
            
        Returns:
            Cosine similarity score (0-1)
        """
        if not query_text or self.domain_embedding is None:
            return 0.0
        
        query_embedding = self.encode(query_text)
        return float(cosine_similarity([query_embedding], [self.domain_embedding])[0][0])
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        return float(cosine_similarity([emb1], [emb2])[0][0])


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        _embedding_service.initialize()
    return _embedding_service
