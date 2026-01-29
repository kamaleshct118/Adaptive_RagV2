"""
LLM Client wrapper for making API calls to OpenAI-compatible endpoints.
"""
import time
import httpx
from typing import Optional
from ..config import get_settings


class LLMClient:
    """Client for interacting with LLM API (Groq, OpenAI, etc.)."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.Client(timeout=30.0)
    
    def call(
        self,
        messages: list[dict],
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Make a call to the LLM API with retry logic for rate limits.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature if provided
            
        Returns:
            Response content string or None if failed
        """
        if not self.settings.llm_api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.settings.llm_model_name,
            "messages": messages,
            "temperature": temperature or self.settings.llm_temperature
        }
        
        for i in range(self.settings.llm_max_retries):
            try:
                response = self.client.post(
                    f"{self.settings.llm_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = 2 * (i + 1)
                    print(f"⚠️ Rate Limit (429). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                print(f"❌ LLM Call Failed: {e}")
                return None
                
            except Exception as e:
                print(f"❌ LLM Call Failed: {e}")
                return None
                
        return None
    
    def __del__(self):
        """Clean up HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
