"""Convergence detection — METRIC-CONVERGENCE-001, EXP-BIAS-001."""

from __future__ import annotations

from typing import List, Optional


def find_convergence_step(
    abs_diffs: List[float],
    rel_diffs: List[float],
    absolute_tolerance: float = 1e-6,
    relative_tolerance: float = 1e-4,
    consecutive_steps_required: int = 3,
) -> Optional[int]:
    """First step after which difference stays below threshold."""
    n = len(abs_diffs)
    if n < consecutive_steps_required:
        return None
    for start in range(n - consecutive_steps_required + 1):
        window_ok = True
        for i in range(start, start + consecutive_steps_required):
            if abs_diffs[i] >= absolute_tolerance or rel_diffs[i] >= relative_tolerance:
                window_ok = False
                break
        if window_ok:
            return start
    return None
