"""Experiment configuration."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal
import yaml

ReversibleMethod = Literal["none", "euler", "midpoint"]

@dataclass
class ModelConfig:
    vocab_size: int = 6144
    n_layer: int = 7
    n_head: int = 7
    n_embd: int = 448
    block_size: int = 256
    tie_weights: bool = True
    target_params: int = 20_000_000
    def validate(self) -> None:
        if self.n_embd % self.n_head:
            raise ValueError("n_embd must be divisible by n_head")
        if self.n_embd % 2:
            raise ValueError("n_embd must be even for reversible blocks")

@dataclass
class TrainingConfig:
    tokens: int = 50_000_000
    batch_size: int = 8
    grad_accumulation: int = 1
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    warmup_steps: int = 200
    log_every: int = 50
    checkpoint_every: int = 0
    def steps_for_tokens(self, seq_len: int) -> int:
        tps = self.batch_size * seq_len * self.grad_accumulation
        return (self.tokens + tps - 1) // tps

@dataclass
class ModeConfig:
    baseline: str = "baseline"
    reversible_method: ReversibleMethod = "none"
    @property
    def is_reversible(self) -> bool:
        return self.reversible_method in ("euler", "midpoint")

@dataclass
class RuntimeConfig:
    device: str = "auto"
    dtype: str = "float32"

@dataclass
class ExperimentConfig:
    experiment_id: str = "session13-reversibility"
    seed: int = 1337
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    mode: ModeConfig = field(default_factory=ModeConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    run_label: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"experiment": {"id": self.experiment_id, "seed": self.seed, "run_label": self.run_label},
                "model": asdict(self.model), "training": asdict(self.training),
                "mode": asdict(self.mode), "runtime": asdict(self.runtime)}

def load_config(path: Path | str) -> ExperimentConfig:
    raw = yaml.safe_load(Path(path).read_text())
    exp, m, t, mo, r = raw.get("experiment", {}), raw.get("model", {}), raw.get("training", {}), raw.get("mode", {}), raw.get("runtime", {})
    cfg = ExperimentConfig(experiment_id=exp.get("id", "session13-reversibility"), seed=int(exp.get("seed", 1337)),
        model=ModelConfig(**{k: m[k] for k in ModelConfig.__dataclass_fields__ if k in m}),
        training=TrainingConfig(**{k: t[k] for k in TrainingConfig.__dataclass_fields__ if k in t}),
        mode=ModeConfig(baseline=mo.get("baseline", "baseline"), reversible_method=mo.get("reversible_method", "none")),
        runtime=RuntimeConfig(**{k: r[k] for k in RuntimeConfig.__dataclass_fields__ if k in r}))
    cfg.model.validate()
    return cfg

def load_config_from_dict(d: dict[str, Any]) -> ExperimentConfig:
    return ExperimentConfig(experiment_id=d["experiment"]["id"], seed=d["experiment"]["seed"],
        run_label=d["experiment"].get("run_label", ""), model=ModelConfig(**d["model"]),
        training=TrainingConfig(**d["training"]), mode=ModeConfig(**d["mode"]), runtime=RuntimeConfig(**d["runtime"]))

def merge_overrides(cfg: ExperimentConfig, **kwargs: Any) -> ExperimentConfig:
    d = cfg.to_dict()
    for key, val in kwargs.items():
        if key == "reversible_method": d["mode"]["reversible_method"] = val
        elif key == "batch_size": d["training"]["batch_size"] = int(val)
        elif key == "tokens": d["training"]["tokens"] = int(val)
        elif key == "seed": d["experiment"]["seed"] = int(val)
        elif key == "run_label": d["experiment"]["run_label"] = str(val)
        elif key in TrainingConfig.__dataclass_fields__: d["training"][key] = val
    return load_config_from_dict(d)
