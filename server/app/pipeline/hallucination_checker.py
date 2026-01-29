"""
Phase 8: Hallucination Checker
Verifies that generated answers are grounded in the source documents.
"""
from ..core.llm import get_llm_client


def check_hallucination(answer: str, contexts: list[str]) -> str:
    """
    Check if the answer contains unsupported claims.
    
    Args:
        answer: The generated answer
        contexts: Source documents used for generation
        
    Returns:
        "YES" if hallucination detected, "NO" otherwise
    """
    llm = get_llm_client()
    
    context_str = "\n".join(contexts)
    prompt = f"Context: {context_str}\nAnswer: {answer}\nUnsupported claims? Output YES or NO."
    
    response = llm.call([{"role": "user", "content": prompt}])
    
    if response and "YES" in response.upper():
        return "YES"
    return "NO"
