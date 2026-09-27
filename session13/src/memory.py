"""Peak memory measurement (host RSS + device allocator)."""
from __future__ import annotations
import resource
import threading
import time
import tracemalloc
from dataclasses import dataclass
import torch

@dataclass
class MemorySnapshot:
    peak_memory_bytes: int
    peak_rss_bytes: int
    peak_mps_bytes: int
    cpu_user_time_s: float
    cpu_system_time_s: float
    label: str = "tracemalloc"
    def to_dict(self) -> dict:
        return {
            "peak_memory_bytes": self.peak_memory_bytes,
            "peak_rss_bytes": self.peak_rss_bytes,
            "peak_mps_bytes": self.peak_mps_bytes,
            "cpu_user_time_s": self.cpu_user_time_s,
            "cpu_system_time_s": self.cpu_system_time_s,
            "memory_label": self.label,
            "peak_rss_gb": self.peak_rss_bytes / (1024 ** 3),
            "peak_mps_gb": self.peak_mps_bytes / (1024 ** 3) if self.peak_mps_bytes else 0.0,
        }

def _rss_bytes() -> int:
    import sys
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Darwin: bytes; Linux: kilobytes
    if sys.platform == "darwin":
        return int(raw)
    return int(raw * 1024)

def _mps_allocated_bytes() -> int:
    if not getattr(torch.backends, "mps", None) or not torch.backends.mps.is_available():
        return 0
    if hasattr(torch.mps, "driver_allocated_memory"):
        return int(torch.mps.driver_allocated_memory())
    return 0

class PeakMemoryTracker:
    def __init__(self, device: torch.device) -> None:
        self.device = device
        self.peak_trace = 0
        self.peak_rss = 0
        self.peak_mps = 0
        self._stop = threading.Event()
        self._thread = None
        self._ru0 = resource.getrusage(resource.RUSAGE_SELF)
        self._label = "unknown"

    def _poll(self) -> None:
        while not self._stop.is_set():
            self.peak_rss = max(self.peak_rss, _rss_bytes())
            self.peak_mps = max(self.peak_mps, _mps_allocated_bytes())
            time.sleep(0.25)

    def __enter__(self):
        self._ru0 = resource.getrusage(resource.RUSAGE_SELF)
        if self.device.type == "cuda":
            torch.cuda.reset_peak_memory_stats(self.device)
            torch.cuda.empty_cache()
            self._label = "cuda_max_memory_allocated"
        elif self.device.type == "mps":
            tracemalloc.start()
            self._label = "mps_driver_allocated_plus_rss"
        else:
            tracemalloc.start()
            self._label = "tracemalloc_plus_rss"
        self.peak_rss = _rss_bytes()
        self.peak_mps = _mps_allocated_bytes()
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.peak_rss = max(self.peak_rss, _rss_bytes())
        self.peak_mps = max(self.peak_mps, _mps_allocated_bytes())
        if self.device.type == "cuda":
            self.peak_trace = int(torch.cuda.max_memory_allocated(self.device))
        else:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self.peak_trace = int(peak)
        self._ru1 = resource.getrusage(resource.RUSAGE_SELF)

    def snapshot(self) -> MemorySnapshot:
        ru = getattr(self, "_ru1", resource.getrusage(resource.RUSAGE_SELF))
        ru0 = getattr(self, "_ru0", ru)
        if self.device.type == "cuda":
            primary = self.peak_trace
        elif self.device.type == "mps" and self.peak_mps > 0:
            primary = self.peak_mps
        else:
            primary = max(self.peak_trace, self.peak_rss)
        return MemorySnapshot(primary, self.peak_rss, self.peak_mps,
            ru.ru_utime - ru0.ru_utime, ru.ru_stime - ru0.ru_stime, self._label)

def estimate_activation_bytes(batch, seq, layers, hidden, dtype_bytes=4, reversible=False):
    per_layer = batch * seq * hidden * dtype_bytes
    if reversible:
        return 2 * (batch * seq * (hidden // 2) * dtype_bytes) * layers
    return per_layer * layers * 4
