"""
Phase 10: Orchestrator Loop (Main Pipeline)
Coordinates all phases of the Adaptive RAG system with retry logic.
"""
import traceback
from typing import Optional
from dataclasses import dataclass, field
from ..config import get_settings
from .query_analyzer import analyze_query
from .relevance_checker import check_relevance
from .safety_validator import validate_rewrite, decide_query_strategy
from .retriever import retrieve_documents, is_kb_covering
from .retrieval_grader import grade_retrieval
from .generator import generate_answer
from .hallucination_checker import check_hallucination
from .final_checker import check_answer_relevance
from .fallback_agent import generate_fallback_response


@dataclass
class PipelineResult:
    """Result from the RAG pipeline execution."""
    answer: str
    category: str = "General"
    tone: str = "Simplified Educational"
    logs: list[str] = field(default_factory=list)
    detailed_trace: list[dict] = field(default_factory=list)
    success: bool = True
    is_fallback: bool = False


def query_reconstructor_pipeline(
    user_query: str,
    feedback_reason: Optional[str] = None
) -> Optional[dict]:
    """
    Phase 4: Central Control Node
    Ties Phases 1, 2, and 3 together.
    
    Args:
        user_query: The user's query
        feedback_reason: Optional feedback from previous retry
        
    Returns:
        Reconstruction result dict or None if failed
    """
    # 1. Analyze
    q_in = f"{user_query} (Fix: {feedback_reason})" if feedback_reason else user_query
    analysis = analyze_query(q_in)
    
    if not analysis:
        return None
    
    # 2. Relevance Check
    is_rel, rel_msg = check_relevance(user_query, analysis)
    if not is_rel:
        return {"is_relevant": False, "logs": [f"Irrelevant: {rel_msg}"]}
    
    # 3. Validate Rewrite
    rewritten = analysis.get('rewritten_query', user_query)
    validation = validate_rewrite(user_query, rewritten)
    
    # 4. Decide Strategy
    final_q, note = decide_query_strategy(user_query, rewritten, validation)
    
    return {
        "is_relevant": True,
        "final_query": final_q,
        "category": analysis.get('category', 'General'),
        "answer_tone": analysis.get('answer_tone', 'Simplified Educational'),
        "logs": [
            f"Category: {analysis.get('category')}",
            f"Tone: {analysis.get('answer_tone')}",
            f"Strategy: {note}",
            f"Final Query: {final_q}"
        ]
    }


def run_adaptive_rag_pipeline(user_query: str) -> PipelineResult:
    """
    Main orchestrator for the Adaptive RAG pipeline.
    
    Executes the full 10-phase pipeline with retry logic:
    1. Query Analysis & Restructuring
    2. Relevance Check
    3. Safety Validation
    4. Central Control
    5. Retrieval
    6. Retrieval Grading
    7. Answer Generation
    8. Hallucination Check
    9. Final Relevance Check
    10. Orchestration Loop
    
    Args:
        user_query: The user's question
        
    Returns:
        PipelineResult with answer, metadata, and logs
    """
    settings = get_settings()
    
    try:
        max_retries = settings.max_pipeline_retries
        attempt = 0
        logs = []
        detailed_trace = []
        feedback_reason = None
        recon = None
        
        while attempt < max_retries:
            attempt += 1
            logs.append(f"\n--- 🔄 Cycle {attempt} ---")
            
            # 1. Reconstruct Query
            recon = query_reconstructor_pipeline(user_query, feedback_reason)
            
            if recon is None:
                logs.append("❌ LLM Service Unavailable (Rate Limit or Error).")
                return PipelineResult(
                    answer="Unable to process query due to high server load. Please try again in 1 minute.",
                    logs=logs,
                    success=False
                )
            
            if not recon or not recon.get('is_relevant'):
                if attempt == 1:
                    logs.extend(recon.get('logs', []))
                    return PipelineResult(
                        answer="I can only answer relevant questions.",
                        logs=logs,
                        success=False
                    )
                else:
                    logs.append("⚠️ Re-evaluated as locally irrelevant. Continuing retry loop...")
                    continue
            
            logs.extend(recon['logs'])
            
            trace_data = {
                "cycle": attempt,
                "analysis": recon,
                "steps": []
            }
            
            # --- PHASE 1-3 LOGGING ---
            trace_data["steps"].append({"name": "Query Analysis", "status": "completed", "data": recon})
            
            # 2. Retrieve Documents
            contexts = retrieve_documents(recon['final_query'])
            # Extract names from formatted strings (Source: name\nContent: ...)
            sources = []
            for ctx in contexts:
                if "Source: " in ctx:
                    sources.append(ctx.split("\n")[0].replace("Source: ", ""))
                else:
                    sources.append("Unknown")
            
            trace_data["steps"].append({"name": "Document Retrieval", "status": "completed", "data": {"count": len(contexts), "sources": sources}})
            
            # 3. KB Coverage Guard
            coverage = is_kb_covering(recon['final_query'], contexts)
            trace_data["steps"].append({"name": "KB Coverage Guard", "status": "completed" if coverage else "failed", "data": {"is_covered": coverage}})
            if not coverage:
                logs.append("⚠️ KB Coverage Failure (Weak Match). Retrying...")
                feedback_reason = "Knowledge Base has no strong match for this specific medical subdomain."
                detailed_trace.append(trace_data)
                continue
            
            # 4. Grade Retrieval
            grade = grade_retrieval(recon['final_query'], contexts)
            trace_data["steps"].append({"name": "Retrieval Grading", "status": "completed" if grade == "GOOD" else "failed", "data": {"grade": grade}})
            if grade == "BAD":
                logs.append("⚠️ Retrieval BAD. Retrying...")
                feedback_reason = "Retrieved documents were irrelevant."
                detailed_trace.append(trace_data)
                continue
            
            # 5. Generate Answer
            answer = generate_answer(
                recon['final_query'],
                contexts,
                recon['category'],
                recon['answer_tone']
            )
            trace_data["steps"].append({"name": "Answer Generation", "status": "completed", "data": {"raw_length": len(answer)}})
            
            # 6. Check Hallucination
            hallucination = check_hallucination(answer, contexts)
            trace_data["steps"].append({"name": "Hallucination Check", "status": "completed", "data": {"is_hallucination": hallucination}})
            if hallucination == "YES":
                logs.append("⚠️ Hallucination detected. Regenerating...")
                answer = generate_answer(
                    recon['final_query'],
                    contexts,
                    recon['category'],
                    recon['answer_tone']
                )
            
            # 7. Check Final Relevance
            final_rel = check_answer_relevance(answer, user_query)
            trace_data["steps"].append({"name": "Final Relevance Check", "status": "completed" if final_rel == "YES" else "failed", "data": {"is_relevant": final_rel}})
            if final_rel == "NO":
                logs.append("⚠️ Answer not relevant. Retrying...")
                feedback_reason = "Answer missed intent."
                detailed_trace.append(trace_data)
                continue
            
            logs.append("✅ Success.")
            detailed_trace.append(trace_data)
            return PipelineResult(
                answer=answer,
                category=recon['category'],
                tone=recon['answer_tone'],
                logs=logs,
                detailed_trace=detailed_trace,
                success=True
            )
        
        # Max retries exhausted - use fallback
        logs.append("\n⚠️ Max retries exhausted. Retrieving Fallback...")
        
        current_category = recon.get('category', 'General') if recon else 'General'
        current_tone = recon.get('answer_tone', 'Simplified Educational') if recon else 'Simplified Educational'
        
        fallback_ans = generate_fallback_response(user_query, current_category, current_tone)
        
        if fallback_ans:
            logs.append("✅ Fallback Generated.")
            return PipelineResult(
                answer=fallback_ans,
                category=current_category,
                tone=current_tone,
                logs=logs,
                success=True,
                is_fallback=True
            )
        
        return PipelineResult(
            answer="❌ Failed to find a valid answer and fallback generation failed.",
            logs=logs,
            success=False
        )
        
    except Exception as e:
        err_msg = f"❌ SYSTEM CRASH: {str(e)}"
        tb = traceback.format_exc().splitlines()
        return PipelineResult(
            answer=err_msg,
            logs=tb,
            success=False
        )
