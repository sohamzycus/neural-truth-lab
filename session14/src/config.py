"""Experiment configuration."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ModelConfig:
    vocab_size: int = 0  # filled from corpus at runtime
    n_layer: int = 3
    n_head: int = 4
    n_embd: int = 128
    block_size: int = 32
    tie_weights: bool = True
    num_experts: int = 4
    top_k: int = 2

    def validate(self) -> None:
        if self.n_embd % self.n_head:
            raise ValueError("n_embd must be divisible by n_head")
        ffn_hidden = 4 * self.n_embd
        if ffn_hidden % self.num_experts:
            raise ValueError("4*n_embd must be divisible by num_experts")
        if self.top_k > self.num_experts:
            raise ValueError("top_k cannot exceed num_experts")

    @property
    def ffn_hidden(self) -> int:
        return 4 * self.n_embd

    @property
    def expert_hidden(self) -> int:
        return self.ffn_hidden // self.num_experts


@dataclass
class TrainingConfig:
    batch_size: int = 8
    learning_rate: float = 3e-3
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    warmup_steps: int = 20
    log_every: int = 10
    dense_steps: int = 300
    moe_steps: int = 300
    eval_batch_seed: int = 4242


@dataclass
class RuntimeConfig:
    device: str = "auto"
    dtype: str = "float32"


@dataclass
class ExperimentConfig:
    experiment_id: str = "session14-dense-to-moe"
    seed: int = 1337
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment": {"id": self.experiment_id, "seed": self.seed},
            "model": asdict(self.model),
            "training": asdict(self.training),
            "runtime": asdict(self.runtime),
        }


def load_config(path: Path | str) -> ExperimentConfig:
    raw = yaml.safe_load(Path(path).read_text())
    exp = raw.get("experiment", {})
    m = raw.get("model", {})
    t = raw.get("training", {})
    r = raw.get("runtime", {})
    cfg = ExperimentConfig(
        experiment_id=exp.get("id", "session14-dense-to-moe"),
        seed=int(exp.get("seed", 1337)),
        model=ModelConfig(**{k: m[k] for k in ModelConfig.__dataclass_fields__ if k in m and k != "vocab_size"}),
        training=TrainingConfig(**{k: t[k] for k in TrainingConfig.__dataclass_fields__ if k in t}),
        runtime=RuntimeConfig(**{k: r[k] for k in RuntimeConfig.__dataclass_fields__ if k in r}),
    )
    cfg.model.validate()
    return cfg
