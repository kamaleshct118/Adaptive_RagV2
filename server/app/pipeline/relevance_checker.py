"""
Phase 2: Relevance Checker (Domain Filter)
Combines embedding similarity with LLM analysis to filter irrelevant queries.
"""
from ..core.embeddings import get_embedding_service


def check_relevance(query: str, llm_analysis_result: dict) -> tuple[bool, str]:
    """
    Check if the query is relevant to the medical domain.
    
    Combines:
    - Embedding similarity to domain text
    - LLM's relevance assessment
    
    Args:
        query: The user's query
        llm_analysis_result: Output from query analyzer
        
    Returns:
        Tuple of (is_relevant, reasoning_message)
    """
    embedding_service = get_embedding_service()
    emb_score = embedding_service.get_domain_relevance(query)
    
    llm_relevant = llm_analysis_result.get('is_relevant', False)
    
    if not llm_relevant:
        return False, f"LLM deemed irrelevant. (Embedding Score: {emb_score:.2f})"
    
    return True, f"Relevant (Embedding Score: {emb_score:.2f})"
