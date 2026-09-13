"""Cosine LR schedule with linear warmup — EXP-SCHEDULE-001."""

from __future__ import annotations

import math

from src.core.schemas import ScheduleConfig


def lr_multiplier(step: int, cfg: ScheduleConfig) -> float:
    """Return LR multiplier at optimizer step (0-indexed)."""
    if step < cfg.warmup_steps:
        return (step + 1) / max(cfg.warmup_steps, 1)
    progress_steps = cfg.total_steps - cfg.warmup_steps
    if progress_steps <= 0:
        return 1.0
    t = (step - cfg.warmup_steps) / progress_steps
    t = min(max(t, 0.0), 1.0)
    cosine = 0.5 * (1.0 + math.cos(math.pi * t))
    return cfg.min_lr_ratio + (1.0 - cfg.min_lr_ratio) * cosine


def warmup_fraction(step: int, cfg: ScheduleConfig) -> float:
    if cfg.warmup_steps <= 0:
        return 1.0
    return min(1.0, (step + 1) / cfg.warmup_steps)
