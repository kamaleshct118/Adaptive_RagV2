# 🏥 Adaptive RAG Server

Production-ready FastAPI backend for the Adaptive RAG medical guideline assistant.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd server
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your LLM_API_KEY
```

### 3. Copy Vector Store
Make sure the `vector_store` directory is in the server folder:
```bash
cp -r ../vector_store ./vector_store
```

### 4. Run the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

### 5. Access the API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 📡 API Endpoints

### `GET /api/health`
Check server and vector store status.

### `POST /api/query`
Process a medical query through the 10-phase RAG pipeline.

**Request:**
```json
{
  "query": "What are the first-line antibiotics for community-acquired pneumonia?"
}
```

**Response:**
```json
{
  "answer": "...",
  "category": "Antibiotic Class Reasoning",
  "tone": "Structured Clinical",
  "is_fallback": false,
  "success": true,
  "logs": ["..."]
}
```

## 🏗️ Architecture

```
server/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Settings management
│   ├── api/
│   │   └── routes.py    # API endpoints
│   ├── core/
│   │   ├── llm.py       # LLM client
│   │   ├── embeddings.py # Sentence Transformers
│   │   └── vector_store.py # FAISS operations
│   └── pipeline/
│       ├── orchestrator.py      # Main 10-phase loop
│       ├── query_analyzer.py    # Phase 1
│       ├── relevance_checker.py # Phase 2
│       ├── safety_validator.py  # Phase 3
│       ├── retriever.py         # Phase 5
│       ├── retrieval_grader.py  # Phase 6
│       ├── generator.py         # Phase 7
│       ├── hallucination_checker.py # Phase 8
│       ├── final_checker.py     # Phase 9
│       └── fallback_agent.py    # Fallback handler
├── vector_store/        # FAISS index + metadata
├── requirements.txt
└── .env.example
```
