"""Update-to-weight ratio — METRIC-RATIO-001, EXP-RATIO-001."""

from __future__ import annotations

EPSILON = 1e-8


def update_to_weight_ratio(update_norm: float, parameter_norm: float) -> float:
    return update_norm / max(parameter_norm, EPSILON)


def detect_warmup_end(warmup_fractions: list[float]) -> int:
    for i, wf in enumerate(warmup_fractions):
        if wf >= 1.0:
            return i
    return len(warmup_fractions) - 1


def detect_stabilization(
    ratios: list[float],
    start_step: int,
    tolerance: float = 0.01,
    consecutive_steps: int = 5,
) -> tuple[int | None, str]:
    """Return (step, rule) or (None, 'NOT_REACHED')."""
    if len(ratios) < start_step + consecutive_steps:
        return None, "NOT_REACHED"
    for i in range(start_step, len(ratios) - consecutive_steps + 1):
        window = ratios[i : i + consecutive_steps]
        mean_r = sum(window) / len(window)
        if all(abs(r - mean_r) / max(mean_r, EPSILON) < tolerance for r in window):
            return i, f"variance_below_{tolerance}_for_{consecutive_steps}_steps"
    return None, "NOT_REACHED"
