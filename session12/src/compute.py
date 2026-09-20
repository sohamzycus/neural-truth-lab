"""Abstract compute work vs simulated GPU time."""

from __future__ import annotations

from dataclasses import dataclass

from .config import SimConfig
from .model import DemoModel


@dataclass
class ComputeResult:
    forward_work: float
    backward_work: float
    optimizer_work: float

    @property
    def total_work(self) -> float:
        return self.forward_work + self.backward_work + self.optimizer_work


def step_compute(model: DemoModel, cfg: SimConfig) -> ComputeResult:
    tokens = cfg.seq_len * cfg.batch_per_gpu
    base = model.logical_parameter_count * tokens * cfg.compute_units_per_param_token
    return ComputeResult(forward_work=base, backward_work=2 * base, optimizer_work=0.25 * base)


def simulated_time_from_work(work: float, cfg: SimConfig) -> float:
    return work * cfg.simulated_seconds_per_compute_unit
