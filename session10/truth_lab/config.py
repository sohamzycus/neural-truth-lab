"""Reproducible lab configuration."""

from __future__ import annotations

import platform
import random
import sys
from dataclasses import dataclass, field

import numpy as np
import torch


@dataclass
class LabConfig:
    seed: int = 1337
    vocab_size: int = 128
    block_size: int = 32
    n_layer: int = 2
    n_head: int = 4
    n_embd: int = 64
    learning_rate: float = 3e-4
    weight_decay: float = 0.0
    grad_clip: float = 1.0
    device: str = field(default_factory=lambda: _pick_device())

    def summary(self) -> dict:
        return {
            "seed": self.seed,
            "device": self.device,
            "python": sys.version.split()[0],
            "pytorch": torch.__version__,
            "platform": platform.platform(),
            "vocab_size": self.vocab_size,
            "block_size": self.block_size,
            "n_layer": self.n_layer,
            "n_head": self.n_head,
            "n_embd": self.n_embd,
        }


def _pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
