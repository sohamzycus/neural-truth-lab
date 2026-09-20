"""Explicit virtual GPU objects — 32 ranks participate in every strategy run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from .config import SimConfig


@dataclass
class VirtualGPU:
    rank: int
    node_id: int
    memory_capacity_bytes: int = 80 * 1024**3  # illustrative cap

    # Ownership: global parameter element indices this rank stores
    param_element_ids: Set[int] = field(default_factory=set)
    grad_element_ids: Set[int] = field(default_factory=set)
    optimizer_element_ids: Set[int] = field(default_factory=set)

    # Metrics accumulated per training step
    communication_bytes: int = 0
    intra_comm_bytes: int = 0
    inter_comm_bytes: int = 0
    compute_work: float = 0.0
    idle_time: float = 0.0
    peak_memory_bytes: int = 0

    # Transient full-parameter view for ZeRO-3 forward/backward
    temp_full_param_elements: int = 0

    def owns_param(self, element_id: int) -> bool:
        return element_id in self.param_element_ids

    def owns_grad(self, element_id: int) -> bool:
        return element_id in self.grad_element_ids

    def owns_optimizer(self, element_id: int) -> bool:
        return element_id in self.optimizer_element_ids


def make_cluster(cfg: SimConfig) -> List[VirtualGPU]:
    gpus: List[VirtualGPU] = []
    for rank in range(cfg.world_size):
        gpus.append(VirtualGPU(rank=rank, node_id=cfg.node_id(rank)))
    return gpus


def shard_elements(total: int, world_size: int, owner: int) -> Set[int]:
    """Partition [0, total) into equal contiguous shards."""
    if total % world_size != 0:
        raise ValueError(f"parameter_count {total} must divide world_size {world_size}")
    per = total // world_size
    start = owner * per
    return set(range(start, start + per))


def replication_map(total: int) -> Dict[int, Set[int]]:
    return {r: set(range(total)) for r in range(total)}  # noqa: unused pattern


def assign_replicated(gpus: List[VirtualGPU], total_elements: int) -> None:
    full = set(range(total_elements))
    for gpu in gpus:
        gpu.param_element_ids = set(full)
        gpu.grad_element_ids = set(full)
        gpu.optimizer_element_ids = set(full)


def assign_zero1_optimizer_shard(gpus: List[VirtualGPU], total_elements: int, world_size: int) -> None:
    full = set(range(total_elements))
    for gpu in gpus:
        gpu.param_element_ids = set(full)
        gpu.grad_element_ids = set(full)
        gpu.optimizer_element_ids = shard_elements(total_elements, world_size, gpu.rank)


def assign_zero2_grad_opt_shard(gpus: List[VirtualGPU], total_elements: int, world_size: int) -> None:
    full = set(range(total_elements))
    for gpu in gpus:
        gpu.param_element_ids = set(full)
        gpu.grad_element_ids = shard_elements(total_elements, world_size, gpu.rank)
        gpu.optimizer_element_ids = shard_elements(total_elements, world_size, gpu.rank)


def assign_zero3_full_shard(gpus: List[VirtualGPU], total_elements: int, world_size: int) -> None:
    for gpu in gpus:
        shard = shard_elements(total_elements, world_size, gpu.rank)
        gpu.param_element_ids = set(shard)
        gpu.grad_element_ids = set(shard)
        gpu.optimizer_element_ids = set(shard)


def count_replication_factor(gpus: List[VirtualGPU], attr: str, total_elements: int) -> int:
    """How many GPUs store each element (max over elements)."""
    from collections import Counter

    c: Counter[int] = Counter()
    for gpu in gpus:
        ids = getattr(gpu, attr)
        for eid in ids:
            c[eid] += 1
    if not c:
        return 0
    return max(c.values())


def sum_shard_coverage(gpus: List[VirtualGPU], attr: str, total_elements: int) -> int:
    covered: Set[int] = set()
    for gpu in gpus:
        covered |= getattr(gpu, attr)
    return len(covered)
