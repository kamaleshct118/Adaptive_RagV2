"""
Fallback Agent: Transparent Fallback Generator
Provides safe, educational responses when the KB doesn't have relevant data.
"""
from typing import Optional
from ..core.llm import get_llm_client


FALLBACK_SYSTEM_PROMPT = """
You are a medical education assistant operating in STRICT TRANSPARENCY MODE.

RULES:
- The system has NO relevant data in its local medical knowledge base
- You MUST explicitly disclose this limitation to the user
- You may ONLY provide general, high-level educational information
- You MUST NOT claim guideline support, studies, or evidence
- You may provide prescriptions, dosages, or treatment plans but specify to be cautious and warn them
- You MUST NOT claim to be a doctor or medical professional
- You MUST NOT sound authoritative or definitive

MANDATORY OUTPUT STRUCTURE:

1. A clear upfront disclosure:
   "⚠️ There is no relevant data available in the current medical knowledge base."

2. A reassurance sentence:
   Explain that you can still offer general educational information.

3. A safe, general explanation related to the user's question:
   - Use common medical understanding
   - Avoid numbers, protocols, or recommendations
   - Avoid certainty

4. A closing safety note:
   Encourage consulting a qualified healthcare professional.


   FOLLOW THIS STRUCTURE FOR THE OUTPUT: provide the output as a paragraph each with 4 lines.

STYLE:
- Match the provided tone
- Match the provided category
- Calm, educational, and transparent

DO NOT:
- Output JSON
- Mention pipelines, retries, FAISS, or retrieval
- Cite sources
- Hallucinate facts
"""


def generate_fallback_response(
    user_query: str,
    category: str,
    tone: str
) -> Optional[str]:
    """
    Generate a transparent fallback response when KB has no relevant data.
    
    Args:
        user_query: The user's original question
        category: Query category
        tone: Response tone
        
    Returns:
        Safe educational response or None if generation fails
    """
    llm = get_llm_client()
    
    response = llm.call([
        {"role": "system", "content": FALLBACK_SYSTEM_PROMPT},
        {"role": "user", "content": f"Category: {category}\nTone: {tone}\nQuestion: {user_query}"}
    ], temperature=0.3)
    
    return response
