"""Performance metrics collection."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MetricsCollector:
    """Collects timing and throughput metrics during training."""

    batch_times: list[float] = field(default_factory=list)
    checkpoint_times: list[float] = field(default_factory=list)
    resume_time: float = 0.0
    replay_time: float = 0.0
    packing_utilization: float = 0.0
    total_useful_tokens: int = 0
    total_padded_tokens: int = 0
    total_batches: int = 0
    total_training_time: float = 0.0

    def record_batch_time(self, elapsed: float) -> None:
        self.batch_times.append(elapsed)

    def record_checkpoint_time(self, elapsed: float) -> None:
        self.checkpoint_times.append(elapsed)

    def set_resume_time(self, elapsed: float) -> None:
        self.resume_time = elapsed

    def set_replay_time(self, elapsed: float) -> None:
        self.replay_time = elapsed

    def set_packing_utilization(self, util: float) -> None:
        self.packing_utilization = util

    def generate_report(self) -> dict[str, Any]:
        avg_batch = sum(self.batch_times) / len(self.batch_times) if self.batch_times else 0.0
        avg_checkpoint = (
            sum(self.checkpoint_times) / len(self.checkpoint_times)
            if self.checkpoint_times
            else 0.0
        )
        total_tokens = self.total_useful_tokens + self.total_padded_tokens
        packing_pct = (
            self.total_useful_tokens / total_tokens * 100 if total_tokens > 0 else 0.0
        )
        training_sec = self.total_training_time or sum(self.batch_times)
        useful_tps = self.total_useful_tokens / training_sec if training_sec > 0 else 0.0
        loss_bearing_tps = self.total_useful_tokens / training_sec if training_sec > 0 else 0.0

        return {
            "packing_utilization_pct": round(packing_pct, 2),
            "avg_packing_utilization": round(self.packing_utilization * 100, 2),
            "useful_tokens_per_sec": round(useful_tps, 2),
            "loss_bearing_tokens_per_sec": round(loss_bearing_tps, 2),
            "replay_time_sec": round(self.replay_time, 4),
            "checkpoint_time_sec": round(avg_checkpoint, 4),
            "resume_time_sec": round(self.resume_time, 4),
            "avg_batch_time_sec": round(avg_batch, 4),
            "total_batches": self.total_batches,
            "total_useful_tokens": self.total_useful_tokens,
            "total_padded_tokens": self.total_padded_tokens,
        }

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.generate_report(), indent=2, sort_keys=True),
            encoding="utf-8",
        )


class Timer:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector | None = None, attr: str = "") -> None:
        self.collector = collector
        self.attr = attr
        self.elapsed = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed = time.perf_counter() - self._start
        if self.collector and self.attr:
            getattr(self.collector, self.attr)(self.elapsed)
