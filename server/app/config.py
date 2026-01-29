"""
Configuration management for the Adaptive RAG Server.
Uses environment variables with sensible defaults.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = "Adaptive RAG API"
    debug: bool = False
    
    # LLM Configuration
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model_name: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.1
    llm_max_retries: int = 2
    
    # Embedding Model
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Vector Store
    vector_store_dir: str = "./vector_store"
    
    # Domain Configuration
    domain_text: str = "Rational antibiotic use, antimicrobial resistance, stewardship, microbiology, guideline-based reasoning"
    
    # RAG Pipeline Settings
    retriever_top_k: int = 3
    kb_coverage_threshold: float = 0.45
    max_pipeline_retries: int = 2
    
    # CORS Settings
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
