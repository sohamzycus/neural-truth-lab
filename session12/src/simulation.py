"""Orchestration helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict

from .config import SimConfig, SINGLE_NODE_INTRA_GBPS, SINGLE_NODE_INTER_GBPS
from .strategies import run_baseline_step, run_zero1_step, run_zero2_step, run_zero3_step
from .strategies.baseline import StepMetrics

RUNNERS: Dict[str, Callable[[SimConfig], StepMetrics]] = {
    "baseline_dp": run_baseline_step,
    "zero1": run_zero1_step,
    "zero2": run_zero2_step,
    "zero3": run_zero3_step,
}


def run_strategy(name: str, cfg: SimConfig) -> StepMetrics:
    return RUNNERS[name](cfg)


def single_node_cfg(base: SimConfig) -> SimConfig:
    return replace(
        base,
        intra_node_bandwidth_gbps=SINGLE_NODE_INTRA_GBPS,
        inter_node_bandwidth_gbps=SINGLE_NODE_INTER_GBPS,
        inter_node_latency_us=base.intra_node_latency_us,
    )
