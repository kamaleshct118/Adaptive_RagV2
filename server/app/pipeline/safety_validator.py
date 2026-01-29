"""
Phase 3: Safety Validator (Rewrite Checker)
Validates that query rewrites don't introduce hallucinations or change meaning.
"""
import json
from ..core.llm import get_llm_client


VALIDATION_SYSTEM_PROMPT = """
You are a query rewrite validator.
Check for ADDED entities, CHANGED constraints, or HALLUCINATIONS.
Output JSON: { "risk_level": "low" | "medium" | "high" }
"""


def validate_rewrite(original: str, rewritten: str) -> dict:
    """
    Validate that the rewritten query preserves the original meaning.
    
    Args:
        original: Original user query
        rewritten: LLM's rewritten version
        
    Returns:
        Dict with 'risk_level': 'low', 'medium', or 'high'
    """
    llm = get_llm_client()
    
    response = llm.call([
        {"role": "system", "content": VALIDATION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Original: {original}\nRewritten: {rewritten}"}
    ], temperature=0.0)
    
    if not response:
        return {"risk_level": "high"}
        
    try:
        clean_resp = response.replace('```json', '').replace('```', '')
        return json.loads(clean_resp)
    except json.JSONDecodeError:
        return {"risk_level": "high"}


def decide_query_strategy(
    original: str,
    rewritten: str,
    validation: dict
) -> tuple[str, str]:
    """
    Decide whether to use the original or rewritten query.
    
    Args:
        original: Original query
        rewritten: Rewritten query
        validation: Validation result with risk_level
        
    Returns:
        Tuple of (chosen_query, decision_reason)
    """
    if original.strip().lower() == rewritten.strip().lower():
        return original, "Identical"
        
    risk = validation.get("risk_level", "high").lower()
    
    if risk in ["medium", "high"]:
        return original, f"Fallback (Risk: {risk})"
        
    return rewritten, "Rewrite Accepted"
