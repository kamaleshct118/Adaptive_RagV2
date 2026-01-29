"""
Phase 5: Retriever using FAISS Vector Search
Also includes KB Coverage Guard (Phase 5b).
"""
from ..core.vector_store import get_vector_store
from ..core.embeddings import get_embedding_service
from ..config import get_settings


def retrieve_documents(query_text: str, k: int | None = None) -> list[str]:
    """
    Retrieve relevant documents from the vector store.
    
    Args:
        query_text: The search query
        k: Number of documents to retrieve
        
    Returns:
        List of formatted document strings
    """
    vector_store = get_vector_store()
    return vector_store.search(query_text, k)


def is_kb_covering(query_text: str, retrieved_contexts: list[str]) -> bool:
    """
    KB Coverage Guard - Check if retrieved documents actually match the query.
    
    Uses semantic similarity to verify that at least one retrieved document
    has sufficient relevance to the query (above threshold).
    
    Args:
        query_text: The user's query
        retrieved_contexts: List of retrieved document strings
        
    Returns:
        True if KB has adequate coverage, False otherwise
    """
    if not retrieved_contexts or not query_text:
        return False
        
    settings = get_settings()
    embedding_service = get_embedding_service()
    
    valid_contexts = [c for c in retrieved_contexts if "[ERROR]" not in c]
    if not valid_contexts:
        return False
        
    try:
        q_vec = embedding_service.encode(query_text)
        max_score = -1.0
        
        for ctx in valid_contexts:
            # Extract content after "Content: " marker if present
            parts = ctx.split("Content: ", 1)
            content = parts[1] if len(parts) > 1 else ctx
            
            # Limit length for speed
            c_vec = embedding_service.encode(content[:1000])
            score = embedding_service.calculate_similarity(query_text, content[:1000])
            
            if score > max_score:
                max_score = score
                
        return max_score >= settings.kb_coverage_threshold
        
    except Exception as e:
        print(f"Coverage check error: {e}")
        # Fail open to avoid blocking valid flows
        return True
