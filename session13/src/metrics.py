"""Experiment metrics collection."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional
import json
from pathlib import Path

@dataclass
class LossPoint:
    tokens: int
    loss: float

@dataclass
class RunMetrics:
    run_id: str
    status: str
    parameter_count: int
    tokens_trained: int
    batch_size: int
    sequence_length: int
    grad_accumulation: int
    training_time_s: float
    tokens_per_sec: float
    final_loss: float
    min_loss: float
    peak_memory_bytes: int
    peak_rss_bytes: int = 0
    peak_mps_bytes: int = 0
    cpu_user_time_s: float = 0.0
    cpu_system_time_s: float = 0.0
    memory_label: str = ""
    device: str = "cpu"
    dtype: str = "float32"
    reversible_method: str = "none"
    seed: int = 0
    timestamp: str = ""
    notes: List[str] = field(default_factory=list)
    loss_history: List[LossPoint] = field(default_factory=list)
    reconstruction_error: Optional[float] = None
    oom: bool = False
    nan: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["loss_history"] = [asdict(p) for p in self.loss_history]
        d["peak_memory_gb"] = self.peak_memory_bytes / (1024 ** 3)
        d["peak_rss_gb"] = self.peak_rss_bytes / (1024 ** 3)
        d["peak_mps_gb"] = self.peak_mps_bytes / (1024 ** 3)
        d["cpu_time_s"] = self.cpu_user_time_s + self.cpu_system_time_s
        return d

def save_run(metrics: RunMetrics, results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "results.json"
    rows: list = []
    if path.exists():
        rows = json.loads(path.read_text())
    rows.append(metrics.to_dict())
    path.write_text(json.dumps(rows, indent=2))
    import csv
    csv_path = results_dir / "results.csv"
    flat = metrics.to_dict()
    flat.pop("loss_history", None)
    flat.pop("notes", None)
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flat.keys()))
        if write_header:
            w.writeheader()
        w.writerow(flat)

def merge_results_for_ui(results_dir: Path, out: Path) -> None:
    src = results_dir / "results.json"
    if not src.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("[]")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(src.read_text())

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
