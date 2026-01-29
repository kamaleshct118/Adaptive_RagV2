"""
Phase 9: Final Relevance Checker
Ensures the answer actually addresses the user's original question.
"""
from ..core.llm import get_llm_client


def check_answer_relevance(answer: str, original_query: str) -> str:
    """
    Check if the answer addresses the original question.
    
    Args:
        answer: The generated answer
        original_query: The user's original question
        
    Returns:
        "YES" if answer is relevant, "NO" otherwise
    """
    llm = get_llm_client()
    
    prompt = f"Query: {original_query}\nAnswer: {answer}\nDoes it answer? Output YES or NO."
    
    response = llm.call([{"role": "user", "content": prompt}])
    
    if response and "YES" in response.upper():
        return "YES"
    return "NO"
