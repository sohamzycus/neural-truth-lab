"""WSD: Warmup → Stable → Decay — EXP-SCHEDULE-001."""

from __future__ import annotations

import math

from src.core.schemas import ScheduleConfig


def lr_multiplier(step: int, cfg: ScheduleConfig) -> float:
    """
    WSD schedule:
      1. Linear warmup: steps [0, warmup_steps)
      2. Stable plateau: steps [warmup_steps, warmup_steps + stable_steps)
      3. Cosine decay: remaining steps down to min_lr_ratio
    """
    if step < cfg.warmup_steps:
        return (step + 1) / max(cfg.warmup_steps, 1)

    stable_end = cfg.warmup_steps + cfg.stable_steps
    if step < stable_end:
        return 1.0

    decay_steps = cfg.decay_steps
    if decay_steps is None:
        decay_steps = max(cfg.total_steps - stable_end, 1)
    t = (step - stable_end) / max(decay_steps, 1)
    t = min(max(t, 0.0), 1.0)
    cosine = 0.5 * (1.0 + math.cos(math.pi * t))
    return cfg.min_lr_ratio + (1.0 - cfg.min_lr_ratio) * cosine


def warmup_fraction(step: int, cfg: ScheduleConfig) -> float:
    if cfg.warmup_steps <= 0:
        return 1.0
    return min(1.0, (step + 1) / cfg.warmup_steps)
