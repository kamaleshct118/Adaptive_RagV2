"""
Phase 6: Retrieval Grader
Evaluates if retrieved documents are actually useful for answering the query.
"""
from ..core.llm import get_llm_client


def grade_retrieval(query: str, contexts: list[str]) -> str:
    """
    Grade the quality of retrieved documents.
    
    Args:
        query: The user's query
        contexts: List of retrieved document strings
        
    Returns:
        "GOOD" if documents are relevant, "BAD" otherwise
    """
    llm = get_llm_client()
    
    context_str = "\n".join(contexts)
    prompt = f"Query: {query}\nContext: {context_str}\nRelevant? Output GOOD or BAD."
    
    response = llm.call([{"role": "user", "content": prompt}])
    
    if response and "GOOD" in response.upper():
        return "GOOD"
    return "BAD"
