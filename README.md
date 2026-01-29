# 🏥 Adaptive RAG System - Production Ready

A production-grade, client-server architecture for the **Adaptive RAG Medical Guideline Assistant**.

## 📚 Architecture Overview

```
adaptiverag/
├── client/          # Next.js 14 Frontend
│   ├── src/app/     # React components & pages
│   └── package.json
├── server/          # FastAPI Backend
│   ├── app/
│   │   ├── api/     # REST endpoints
│   │   ├── core/    # LLM, embeddings, vector store
│   │   └── pipeline/ # 10-phase RAG logic
│   └── requirements.txt
├── Documents/       # Source PDFs (medical guidelines)
├── vector_store/    # FAISS index (generated)
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Groq API key (or OpenAI-compatible LLM API)

### 1. Setup Backend

```bash
cd server

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env and add your LLM_API_KEY

# Copy vector store
xcopy ..\vector_store vector_store /E /I  # Windows
# cp -r ../vector_store ./vector_store  # Linux/Mac

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

---

## 🔄 The 10-Phase Adaptive Pipeline

Every query passes through this rigorous verification pipeline:

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Query Analyzer | Understand intent, category, and tone |
| 2 | Relevance Checker | Filter out-of-domain queries |
| 3 | Safety Validator | Verify rewrite preserves meaning |
| 4 | Central Control | Decide query strategy |
| 5 | Retriever | FAISS vector search + KB coverage guard |
| 6 | Retrieval Grader | Verify document quality |
| 7 | Generator | Tone-aware answer generation |
| 8 | Hallucination Checker | Fact-check against sources |
| 9 | Final Checker | Verify answer addresses query |
| 10 | Orchestrator | Retry loop with fallback |

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

This starts:
- Backend on `http://localhost:8000`
- Frontend on `http://localhost:3000`

---

## 📁 Original Notebooks (Reference)

The original Jupyter notebooks are preserved for reference:
- `Adaptive__Rag.ipynb` - Interactive demo with Gradio
- `offline_indexing_pipeline.ipynb` - Document indexing pipeline

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | Your Groq/OpenAI API key | (required) |
| `LLM_BASE_URL` | LLM API endpoint | `https://api.groq.com/openai/v1` |
| `LLM_MODEL_NAME` | Model to use | `llama-3.3-70b-versatile` |
| `VECTOR_STORE_DIR` | Path to FAISS index | `./vector_store` |

---

## 📝 License

This project is for educational purposes in antimicrobial stewardship.
