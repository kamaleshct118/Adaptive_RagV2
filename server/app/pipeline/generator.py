"""
Phase 7: Answer Generator (Tone-Aware)
Generates the final answer using retrieved context with appropriate tone.
"""
from typing import Optional
from ..core.llm import get_llm_client


def generate_answer(
    query: str,
    contexts: list[str],
    category: str,
    tone: str
) -> Optional[str]:
    """
    Generate an answer using the retrieved context.
    
    Args:
        query: The user's query
        contexts: List of retrieved document strings
        category: The query category (e.g., "Infection Context")
        tone: The response tone (e.g., "Simplified Educational")
        
    Returns:
        Generated answer string or None if generation fails
    """
    llm = get_llm_client()
    
    context_str = "\n".join(contexts)
    system_prompt = f"Educational medical assistant. Category: {category}. Tone: {tone}. No prescriptions."
    
    response = llm.call([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context_str}\nQuestion: {query}"}
    ])
    
    return response
