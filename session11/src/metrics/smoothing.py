"""Loss smoothing — METRIC-LR-001."""

from __future__ import annotations

from typing import List


def smoothed_tail(values: List[float], window: int = 5) -> float:
    valid = [v for v in values if v == v]  # drop NaN
    if not valid:
        return float("nan")
    tail = valid[-window:]
    return sum(tail) / len(tail)
