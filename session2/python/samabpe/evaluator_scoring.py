"""Backward-compatible re-exports — use evaluator_contract.py."""

from samabpe.evaluator_contract import (  # noqa: F401
    HINDI_FERTILITY_THRESHOLD,
    LANGS,
    EvaluatorMetrics,
    calculate_scores,
    compute_evaluator_metrics,
    fertility,
    hindi_penalty,
)
