# 🏥 Adaptive Learning Assistant (Rational Antimicrobial Use)

**A production-grade, offline-first Adaptive RAG system for medical guideline stewardship.**

## 📚 Project Structure
This project consists of **two** distinct notebooks that work together:

### 1. `offline_indexing_pipeline.ipynb` (The Prep Work)
**Goal**: Convert raw medical guidelines (PDF/Text) into a searchable mathematical index.
-   **Step 1**: Reads text chunks from documents.
-   **Step 2**: Embeds them using `sentence-transformers/all-MiniLM-L6-v2`.
-   **Step 3**: Saves a **Local FAISS Index** (`index.faiss`) + Metadata (`metadata.pkl`) into the `./vector_store/` folder.
-   *Note: This runs once, offline. No API keys needed.*

### 2. `Adaptive__Rag.ipynb` (The Intelligence)
**Goal**: Answer user questions by intelligently retrieving info from the pre-built index.
-   **Goal**: Adaptive, Tone-Aware, Hallucination-Free answers.
-   **Input**: User Query.
-   **Output**: Verified Answer + Logs.

---

## 🔄 The 10-Phase Execution Workflow
Every query sent to `Adaptive__Rag.ipynb` follows this strict linear path. This architecture ensures that **Retrieval is dumb/fast** while **Control is smart/adaptive**.

### 🎮 Control Plane (Logic)
**Phase 10: Orchestrator Loop**
*   The Manager. It starts the cycle and handles retries if something goes wrong.

**Phase 4: Central Control Node**
*   The "Brain" of the operation. It coordinates Phases 1-3 to prepare the perfect query.

**Phase 1: Query Analysis & Restructuring (LLM)**
*   Analyzes the user's raw question.
*   Determines **Intent**, **Category** (e.g., Side Effects vs Mechanism), and **Tone** (Educational vs Clinical).
*   Proposes a **Rewritten Query** optimized for search.

**Phase 2: Relevance Check (Domain Filter)**
*   Mathematical Gatekeeper.
*   Calculates `CosineSimilarity(Query, Medical_Domain)`. If it's 0.1 (low), we block the query as spam.

**Phase 3: Safety Validation (Rewrite Checker)**
*   The Critic.
*   Checks if the "Rewritten Query" from Phase 1 is safe. Did the LLM add fake info? If yes, we fallback to the original query.

---

### 💾 Data Plane (Retrieval)
**Phase 5: Retriever (FAISS Vector Search)**
*   **The Only Retrieval Step**.
*   Takes the verified string -> Embeds it -> Finds Top-3 matching chunks from the offline index.

**Phase 6: Retrieval Grader (Quality Check)**
*   Reads the retrieved chunks.
*   Asks: *"Do these actually answer the question?"*
*   If **BAD**, the Orchestrator triggers a retry loop.

---

### ✍️ Generation & Verification
**Phase 7: Answer Generator (Tone-Aware)**
*   The Writer.
*   Generates the answer using the retrieved context.
*   **Tone Matching**: Adapts style based on Phase 1 (e.g., "Explain like I'm a student" vs "Give list of contraindications").

**Phase 8: Hallucination Checker**
*   Fact Verification.
*   Compares the Answer vs the Context. If the answer contains "new" facts not in the context, it rejects it.

**Phase 9: Final Relevance Checker**
*   Alignment Check.
*   Ensures the final answer actually responds to the user's specific question.

**Phase 13: Final Verified Answer**
*   Success! The answer is displayed to the user.

---

## 🚀 How to Run
1.  **Run Notebook 1 (`offline_indexing_pipeline`)** to generate the `vector_store` folder.
2.  **Open Notebook 2 (`Adaptive__Rag`)**.
3.  **Upload** the `vector_store` folder to the file execution area.
4.  **Enter API Key**: You need an OpenAI-compatible key (e.g., Groq) for the LLM agents.
5.  **Run All Cells**: The interface will launch at the bottom.
