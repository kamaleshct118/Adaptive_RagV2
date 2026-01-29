"""
Phase 1: Query Analysis & Restructuring Agent
Analyzes user queries to understand intent, category, tone, and rewrites for better retrieval.
"""
import json
from typing import Optional
from ..core.llm import get_llm_client


ANALYSIS_SYSTEM_PROMPT = """
You are a query analysis and restructuring engine for an Adaptive RAG system.
CRITICAL RULES:
- Query rewriting MUST be LOSSLESS.
- Do NOT add entities, tools, datasets, years, domains, or assumptions.
- Output VALID JSON ONLY.

REQUIRED JSON OUTPUT CONTRACT:
{
  "is_relevant": true,
  "category": "<Infection Context Explanation|Antibiotic Class Reasoning|Resistance Mechanism|Stewardship Principle|Safety / Adverse Effects|Guideline Explanation>",
  "answer_tone": "<Simplified Educational|Structured Clinical>",
  "original_query": "...",
  "rewritten_query": "...",
  "rewrite_rationale": "..."
}
"""


def analyze_query(user_query: str) -> Optional[dict]:
    """
    Analyze and restructure the user query for optimal retrieval.
    
    Args:
        user_query: The user's original question
        
    Returns:
        Analysis dict with category, tone, rewritten query, etc.
        None if LLM call fails
    """
    llm = get_llm_client()
    
    response = llm.call([
        {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": f"Query: {user_query}"}
    ], temperature=0.1)
    
    if not response:
        return None
        
    try:
        clean_resp = response.replace('```json', '').replace('```', '')
        return json.loads(clean_resp)
    except json.JSONDecodeError:
        # Return safe defaults if JSON parsing fails
        return {
            "is_relevant": True,
            "category": "General",
            "answer_tone": "Simplified Educational",
            "original_query": user_query,
            "rewritten_query": user_query
        }
