"""
API Routes for the Adaptive RAG Server.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..pipeline import run_adaptive_rag_pipeline
from ..core.vector_store import get_vector_store


router = APIRouter()


# ============ Request/Response Models ============

class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the first-line antibiotics for community-acquired pneumonia?"
            }
        }


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    answer: str
    category: str
    tone: str
    is_fallback: bool
    success: bool
    logs: Optional[list[str]] = None
    detailed_trace: Optional[list[dict]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_count: int
    message: str


# ============ Endpoints ============

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Check if the server is running and the vector store is loaded.
    """
    try:
        vector_store = get_vector_store()
        vector_count = vector_store.total_vectors
        
        if vector_count > 0:
            return HealthResponse(
                status="healthy",
                vector_count=vector_count,
                message="Server is running and vector store is loaded."
            )
        else:
            return HealthResponse(
                status="degraded",
                vector_count=0,
                message="Server is running but vector store is empty."
            )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            vector_count=0,
            message=f"Vector store error: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse, tags=["RAG"])
async def process_query(request: QueryRequest):
    """
    Process a medical query through the Adaptive RAG pipeline.
    
    The query goes through a 10-phase verification pipeline:
    1. Query Analysis & Restructuring
    2. Domain Relevance Check
    3. Safety Validation
    4. Central Control
    5. FAISS Retrieval
    6. Retrieval Grading
    7. Answer Generation
    8. Hallucination Check
    9. Final Relevance Check
    10. Orchestration with retries
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    result = run_adaptive_rag_pipeline(request.query)
    
    return QueryResponse(
        answer=result.answer,
        category=result.category,
        tone=result.tone,
        is_fallback=result.is_fallback,
        success=result.success,
        logs=result.logs,
        detailed_trace=result.detailed_trace
    )


@router.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Adaptive RAG API",
        "version": "1.0.0",
        "description": "Production-ready Adaptive RAG system for medical guideline stewardship",
        "endpoints": {
            "health": "/api/health",
            "query": "/api/query (POST)"
        }
    }
