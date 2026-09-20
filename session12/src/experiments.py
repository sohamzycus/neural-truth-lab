"""Experiment matrix — records measurable simulator output."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import List

from .config import SimConfig, WORLD_SIZE
from .simulation import run_strategy, single_node_cfg


@dataclass
class ExperimentRecord:
    experiment_id: str
    strategy: str
    world_size: int
    model_parameters: int
    memory_per_gpu: int
    peak_memory_per_gpu: int
    aggregate_memory: int
    compute_work: float
    communication_bytes: int
    communication_time: float
    compute_time: float
    total_step_time: float
    communication_fraction: float
    notes: str = ""


def _record(exp_id: str, m, cfg: SimConfig, notes: str = "") -> ExperimentRecord:
    return ExperimentRecord(
        experiment_id=exp_id,
        strategy=m.strategy,
        world_size=cfg.world_size,
        model_parameters=cfg.parameter_count,
        memory_per_gpu=m.aggregate_memory // cfg.world_size,
        peak_memory_per_gpu=m.peak_memory_per_gpu,
        aggregate_memory=m.aggregate_memory,
        compute_work=m.compute_work,
        communication_bytes=m.communication_bytes,
        communication_time=m.communication_time,
        compute_time=m.compute_time,
        total_step_time=m.total_step_time,
        communication_fraction=m.communication_fraction,
        notes=notes,
    )


def run_all_experiments(base: SimConfig | None = None) -> List[ExperimentRecord]:
    base = base or SimConfig()
    records: List[ExperimentRecord] = []

    for i, strat in enumerate(["baseline_dp", "zero1", "zero2", "zero3"], start=1):
        m = run_strategy(strat, base)
        records.append(_record(f"exp{i}_{strat}", m, base))

    sn = single_node_cfg(base)
    m5 = run_strategy("zero3", sn)
    records.append(_record("exp5_single_node_zero3", m5, sn, "single-node comm assumption"))

    m6 = run_strategy("zero3", base)
    records.append(_record("exp6_multi_node_zero3", m6, base, "multi-node default topology"))

    for bucket, eid in [(50_000_000, "exp7_bucket_large"), (500_000, "exp7_bucket_small")]:
        cfg_b = replace(base, bucket_size_bytes=bucket)
        m = run_strategy("zero3", cfg_b)
        records.append(_record(eid, m, cfg_b, f"bucket_size={bucket}"))

    for params, eid in [(500_000, "exp8_small"), (2_000_000, "exp8_medium"), (8_000_000, "exp8_large")]:
        if params % WORLD_SIZE != 0:
            params += WORLD_SIZE - (params % WORLD_SIZE)
        cfg_s = replace(base, parameter_count=params)
        m = run_strategy("zero3", cfg_s)
        records.append(_record(eid, m, cfg_s, "model size sweep"))

    return records


def scaling_sweep(base: SimConfig | None = None) -> List[ExperimentRecord]:
    base = base or SimConfig()
    out = []
    for ws in [1, 2, 4, 8, 16, 32]:
        if base.parameter_count % ws != 0:
            continue
        cfg = replace(base, world_size=ws, gpus_per_node=min(8, ws))
        m = run_strategy("baseline_dp", cfg)
        out.append(_record(f"scaling_ws{ws}", m, cfg, "baseline scaling"))
    return out


def save_records(records: List[ExperimentRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump([asdict(r) for r in records], f, indent=2)
