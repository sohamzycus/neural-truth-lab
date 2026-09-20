"""Collective communication simulator — simulation assumptions, not HW benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .config import SimConfig


@dataclass
class CommResult:
    operation: str
    bytes_moved: int
    intra_node_bytes: int
    inter_node_bytes: int
    simulated_time_s: float
    participating_ranks: Sequence[int]

    def label(self) -> str:
        return "Simulation assumption — not measured NVIDIA performance"


def _pairwise_bytes(cfg: SimConfig, ranks: Sequence[int], element_bytes: int) -> tuple[int, int]:
    """Approximate intra vs inter bytes for ring-style collective."""
    intra = 0
    inter = 0
    n = len(ranks)
    if n <= 1:
        return 0, 0
    # each rank sends ~2*(n-1)/n of payload in all-reduce (ring model)
    per_rank_send = int(2 * (n - 1) / n * element_bytes)
    for i, r in enumerate(ranks):
        nxt = ranks[(i + 1) % n]
        if cfg.same_node(r, nxt):
            intra += per_rank_send
        else:
            inter += per_rank_send
    return intra, inter


def _time_from_bytes(cfg: SimConfig, intra: int, inter: int, steps: int = 1) -> float:
    intra_gbps = cfg.intra_node_bandwidth_gbps * 1e9
    inter_gbps = cfg.inter_node_bandwidth_gbps * 1e9
    t_intra = intra / intra_gbps if intra else 0.0
    t_inter = inter / inter_gbps if inter else 0.0
    lat = (cfg.intra_node_latency_us + cfg.inter_node_latency_us) * 1e-6 * steps
    return max(t_intra, t_inter) + lat


def all_reduce(cfg: SimConfig, ranks: List[int], tensor_bytes: int) -> CommResult:
    # Teaching approximation: ring all-reduce moves ~2× the payload across the network.
    n = len(ranks)
    moved = 2 * tensor_bytes if n > 1 else 0
    intra, inter = _pairwise_bytes(cfg, ranks, moved // max(n, 1))
    # rescale pairwise estimate to match moved total
    scale = moved / max(intra + inter, 1)
    intra, inter = int(intra * scale), int(inter * scale)
    t = _time_from_bytes(cfg, intra, inter, steps=2 * (n - 1))
    return CommResult("all_reduce", moved, intra, inter, t, ranks)


def reduce_scatter(cfg: SimConfig, ranks: List[int], tensor_bytes: int) -> CommResult:
    n = len(ranks)
    moved = tensor_bytes if n > 1 else 0
    intra, inter = _pairwise_bytes(cfg, ranks, moved // max(n, 1))
    scale = moved / max(intra + inter, 1)
    intra, inter = int(intra * scale), int(inter * scale)
    t = _time_from_bytes(cfg, intra, inter, steps=n - 1)
    return CommResult("reduce_scatter", moved, intra, inter, t, ranks)


def all_gather(cfg: SimConfig, ranks: List[int], shard_bytes: int) -> CommResult:
    n = len(ranks)
    full = shard_bytes * n
    moved = full if n > 1 else 0
    intra, inter = _pairwise_bytes(cfg, ranks, moved // max(n, 1))
    scale = moved / max(intra + inter, 1)
    intra, inter = int(intra * scale), int(inter * scale)
    t = _time_from_bytes(cfg, intra, inter, steps=n - 1)
    return CommResult("all_gather", moved, intra, inter, t, ranks)


def apply_comm_to_gpus(gpus, result: CommResult) -> None:
    for gpu in gpus:
        if gpu.rank in result.participating_ranks:
            gpu.communication_bytes += result.bytes_moved // len(result.participating_ranks)
            gpu.intra_comm_bytes += result.intra_node_bytes // len(result.participating_ranks)
            gpu.inter_comm_bytes += result.inter_node_bytes // len(result.participating_ranks)


def overlap_adjusted_time(
    comm_time: float, compute_time: float, bucket_size: int, total_tensor_bytes: int, overlap_fraction: float
) -> float:
    """Conceptual overlap simulation — not DeepSpeed's scheduler."""
    if total_tensor_bytes <= 0 or bucket_size <= 0:
        return comm_time
    num_buckets = max(1, (total_tensor_bytes + bucket_size - 1) // bucket_size)
    per_bucket_comm = comm_time / num_buckets
    # overlap_fraction of each bucket can hide under compute
    hidden = min(compute_time, num_buckets * per_bucket_comm * overlap_fraction)
    return max(0.0, comm_time - hidden)
