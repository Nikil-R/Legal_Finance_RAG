"""
RAGAS Evaluation endpoint.
POST /api/v2/evaluate          — evaluate a single response
POST /api/v2/evaluate/batch    — run the full curated test suite
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.api.security import AuthenticatedUser, require_role
from app.evaluation.ragas_eval import EVAL_DATASET, RAGASEvaluator
from app.generation.pipeline import RAGPipeline
from app.models.auth import Role
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Evaluation"])

# Lazy singleton evaluator
_evaluator: Optional[RAGASEvaluator] = None


def _get_evaluator() -> RAGASEvaluator:
    global _evaluator
    if _evaluator is None:
        _evaluator = RAGASEvaluator()
    return _evaluator


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class EvalRequest(BaseModel):
    question: str
    answer: str
    contexts: List[str] = Field(default_factory=list)
    ground_truth: Optional[str] = None
    domain: str = "all"
    model: str = "unknown"
    latency_ms: float = 0.0


class EvalResponse(BaseModel):
    success: bool
    metrics: Dict[str, Any]
    overall_score: float
    passed: bool


class BatchEvalRequest(BaseModel):
    """
    Optional: caller can supply their own samples.
    If omitted, the built-in EVAL_DATASET is used.
    The pipeline is used to generate answers for each question.
    """
    use_pipeline: bool = True   # auto-generate answers via RAGPipeline
    domain: str = "all"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=EvalResponse)
async def evaluate_single(
    req: EvalRequest,
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.ADMIN)),
) -> EvalResponse:
    """Evaluates one question-answer pair with RAGAS metrics."""
    try:
        ev = _get_evaluator()
        result = await run_in_threadpool(
            ev.evaluate,
            question=req.question,
            answer=req.answer,
            contexts=req.contexts,
            ground_truth=req.ground_truth,
            domain=req.domain,
            model=req.model,
            latency_ms=req.latency_ms,
        )
        return EvalResponse(
            success=True,
            metrics=result.to_dict()["metrics"],
            overall_score=result.overall_score,
            passed=result.passed,
        )
    except Exception as e:
        logger.error("Evaluation error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def evaluate_batch(
    req: BatchEvalRequest,
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.ADMIN)),
) -> Dict[str, Any]:
    """
    Runs RAGAS evaluation over the curated legal/finance test dataset.
    If use_pipeline=True (default), answers are generated live via the RAG pipeline.
    """
    try:
        ev = _get_evaluator()
        samples: List[Dict[str, Any]] = []

        if req.use_pipeline:
            pipeline = RAGPipeline()
            logger.info("RAGAS batch eval: generating answers for %d samples…", len(EVAL_DATASET))

            async def _run_sample(item: Dict[str, Any]) -> Dict[str, Any]:
                import time
                q = item["question"]
                domain = item.get("domain", req.domain)
                t0 = time.perf_counter()
                result = await run_in_threadpool(
                    pipeline.run,
                    question=q,
                    domain=domain,
                    session_id=None,
                    owner_id=None,
                )
                latency_ms = (time.perf_counter() - t0) * 1000
                if result.get("success"):
                    contexts = [
                        s.get("content", s.get("excerpt", ""))
                        for s in result.get("sources", [])
                        if isinstance(s, dict)
                    ]
                    return {
                        "question": q,
                        "answer": result["answer"],
                        "contexts": contexts,
                        "ground_truth": item.get("ground_truth"),
                        "domain": domain,
                        "model": result.get("metadata", {}).get("model", "unknown"),
                        "latency_ms": latency_ms,
                    }
                return {
                    "question": q,
                    "answer": result.get("error", "No answer"),
                    "contexts": [],
                    "ground_truth": item.get("ground_truth"),
                    "domain": domain,
                    "latency_ms": latency_ms,
                }

            # Run samples concurrently (capped at 3 parallel to avoid rate limits)
            semaphore = asyncio.Semaphore(3)

            async def _safe_run(item: Dict[str, Any]) -> Dict[str, Any]:
                async with semaphore:
                    return await _run_sample(item)

            samples = await asyncio.gather(*[_safe_run(d) for d in EVAL_DATASET])
        else:
            # No pipeline: just run eval on empty contexts (dry run)
            samples = [
                {
                    "question": d["question"],
                    "answer": d.get("ground_truth", ""),
                    "contexts": [d.get("ground_truth", "")],
                    "ground_truth": d.get("ground_truth"),
                    "domain": d.get("domain", req.domain),
                }
                for d in EVAL_DATASET
            ]

        batch_result = await run_in_threadpool(ev.evaluate_batch, samples)

        logger.info(
            "RAGAS batch complete | faithfulness=%.2f | relevancy=%.2f | precision=%.2f | pass_rate=%.0f%%",
            batch_result.avg_faithfulness,
            batch_result.avg_answer_relevancy,
            batch_result.avg_context_precision,
            batch_result.pass_rate * 100,
        )

        return {
            "success": True,
            **batch_result.summary(),
        }

    except Exception as e:
        logger.error("Batch evaluation error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
