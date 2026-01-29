# 🏥 Adaptive Learning Assistant (Rational Antimicrobial Use)

**A production-grade, offline-first Adaptive RAG system for medical guideline stewardship.**

## 📚 Project Architecture
This project uses a **Two-Notebook Architecture** to separate data engineering from inference:

### 1. `offline_indexing_pipeline.ipynb` (The Factory)
**Role**: Data Preprocessing & Indexing.
**Status**: Run Once (Offline).
**Process**:
-   **Ingest**: Reads PDFs/Images from `./raw_documents`.
-   **Digitize**: Uses Tesseract OCR to extract text.
-   **Chunk**: Splits text into sliding windows (400 chars).
-   **Embed**: Converts text to vectors using `all-MiniLM-L6-v2`.
-   **Index**: Saves a FAISS index to `./vector_store`.

### 2. `Adaptive__Rag.ipynb` (The Brain)
**Role**: Inference & answering.
**Status**: Run Anytime (Interative).
**Process**:
-   **Load**: Mounts the `./vector_store`.
-   **Think**: Uses a 12-Step Adaptive Pipeline.
-   **Answer**: Provides cited, safe medical answers.

---

## 🔄 The 12-Phase Adaptive Workflow
Every query passes through this rigorous verification pipeline.

### 🎮 Control Plane (Logic)
**Phase 10: Orchestrator Loop**
*   The Manager. Runs the retry loop (Max 2 attempts).
*   Manages error handling (Rate Limits) and Fallback triggering.

**Phase 4: Central Control Node**
*   The Strategy Maker. Decides whether to use the user's raw query or a refined version.

**Phase 1: Query Analysis & Restructuring**
*   **Agent**: LLM
*   **Goal**: Understand Intent, Category, and Tone.
*   **Output**: A "Rewritten Query" optimized for vector search.

**Phase 2: Relevance Check (Domain Filter)**
*   **Agent**: Embedding Model + LLM
*   **Goal**: Block irrelevant questions (e.g., "How to bake a cake") early.

**Phase 3: Safety Validation**
*   **Agent**: Critical LLM
*   **Goal**: Ensure the "Rewritten Query" didn't lose the original meaning or hallucinate.

### 💾 Data Plane (Retrieval)
**Phase 5: Retriever (FAISS)**
*   **Tool**: Vector Search
*   **Goal**: Find top-3 matching document chunks.

**Phase 5b: KB Coverage Guard (NEW)**
*   **Tool**: Semantic Similarity Check
*   **Goal**: **Fail Fast**. If the retrieved chunks have low similarity (< 0.45) to the query, we reject them immediately as "Noise" and trigger a retry.

**Phase 6: Retrieval Grader**
*   **Agent**: LLM
*   **Goal**: Read the text. Does it *actually* contain the answer? If no, retry.

### ✍️ Generation & Verification
**Phase 7: Answer Generator**
*   **Agent**: Tone-Aware LLM
*   **Goal**: Write the answer using *only* the provided context. Adapts tone (Educational vs Clinical).

**Phase 8: Hallucination Checker**
*   **Agent**: LLM
*   **Goal**: Fact-check the answer against the documents.

**Phase 9: Final Relevance Checker**
*   **Agent**: LLM
*   **Goal**: Ensure the answer addresses the user's original specific question.

### 🚑 Safety Net
**Phase 11: Transparent Fallback Agent (NEW)**
*   **Trigger**: If all Retries fail or the KB Guard blocks everything.
*   **Goal**: Provide general medical education with strict "No Knowledge Base" warnings, ensuring the user always gets a helpful (but safe) response.

---

## 🚀 How to Run
1.  **Setup**: Install dependencies (`requirements.txt`).
2.  **Index**: Run `offline_indexing_pipeline.ipynb` to create your database.
3.  **Launch**: Run `Adaptive__Rag.ipynb`.
4.  **Interact**: Use the Gradio UI at the bottom of the notebook.
