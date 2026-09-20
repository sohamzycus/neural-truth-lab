"""Small demo model — real micro-tensors, memory sized from parameter_count."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import SimConfig


@dataclass
class DemoModel:
    cfg: SimConfig
    layers: list[np.ndarray]

    @classmethod
    def build(cls, cfg: SimConfig) -> "DemoModel":
        # Tiny tensors; logical parameter_count may be larger (memory uses cfg)
        d = cfg.hidden_dim
        layers = [np.random.randn(d, d).astype(np.float32) * 0.02 for _ in range(cfg.num_layers)]
        return cls(cfg=cfg, layers=layers)

    @property
    def logical_parameter_count(self) -> int:
        return self.cfg.parameter_count

    def forward_backward(self, rank: int) -> float:
        """Minimal real compute; returns abstract compute_work units."""
        x = np.random.randn(self.cfg.hidden_dim).astype(np.float32)
        for w in self.layers:
            x = np.tanh(x @ w)
        # tie to logical model size
        tokens = self.cfg.seq_len * self.cfg.batch_per_gpu
        work = self.logical_parameter_count * tokens * self.cfg.compute_units_per_param_token
        # backward ~2x forward in this toy model
        return work * 3.0
