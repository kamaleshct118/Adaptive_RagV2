"""
Adaptive RAG Server - FastAPI Application Entry Point

Production-ready API for the Adaptive RAG medical guideline assistant.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api import router
from .core.embeddings import get_embedding_service
from .core.vector_store import get_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    Initializes heavy resources (models, vector store) at startup.
    """
    print("🚀 Starting Adaptive RAG Server...")
    
    # Initialize services at startup
    print("📦 Loading embedding model...")
    get_embedding_service()
    
    print("📂 Loading vector store...")
    get_vector_store()
    
    print("✅ Server ready!")
    
    yield
    
    # Cleanup on shutdown
    print("👋 Shutting down server...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="""
# 🏥 Adaptive RAG API

A production-ready Adaptive RAG system for **medical guideline stewardship**.

## Features
- **10-Phase Verification Pipeline** for accurate, safe responses
- **Hallucination Detection** to ensure factual accuracy
- **Tone-Aware Generation** (Educational vs Clinical)
- **Transparent Fallback** when knowledge base has no coverage

## Usage
Send a POST request to `/api/query` with your medical question.
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
