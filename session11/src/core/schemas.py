"""Typed schemas — SPEC: data_contracts.yaml, experiment_spec.yaml"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class ClaimStatus(str, Enum):
    UNTESTED = "UNTESTED"
    SUPPORTED = "SUPPORTED"
    WEAKLY_SUPPORTED = "WEAKLY_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REFUTED = "REFUTED"
    NOT_REACHED = "NOT_REACHED"
    INVALID_EXPERIMENT = "INVALID_EXPERIMENT"


@dataclass
class ModelConfig:
    seed: int = 1337
    vocab_size: int = 128
    block_size: int = 32
    n_layer: int = 2
    n_head: int = 4
    n_embd: int = 64
    width: Optional[int] = None  # alias for n_embd when sweeping

    def __post_init__(self) -> None:
        if self.width is not None:
            self.n_embd = self.width

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OptimizerConfig:
    name: str = "AdamW"
    learning_rate: float = 3e-4
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    weight_decay: float = 0.0
    bias_correction: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScheduleConfig:
    name: str = "wsd"
    warmup_steps: int = 10
    stable_steps: int = 0
    total_steps: int = 300
    min_lr_ratio: float = 0.1
    decay_steps: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataConfig:
    batch_size: int = 2
    seed_offset: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeConfig:
    device: str = "cpu"
    grad_clip: float = 1.0
    dtype: str = "float32"
    grad_accumulation: int = 1
    execution_mode: str = "full"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentSpec:
    id: str
    claim_id: str
    title: str
    hypothesis: str
    objective: str
    controls: list[str]
    independent_variable: str
    dependent_variables: list[str]
    protocol: str
    acceptance_criteria: dict[str, Any]
    expected_artifacts: list[str]
    reproducibility_command: str
    status: str = "UNTESTED"


@dataclass
class MetricRecord:
    metric_id: str
    value: Any
    label: str  # MEASURED, CALCULATED, etc.
    unit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionRecord:
    decision_id: str
    claim_id: str
    status: ClaimStatus
    confidence: str
    rationale: str
    thresholds_used: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class EvidenceRecord:
    evidence_id: str
    experiment_id: str
    claim_id: str
    hypothesis: str
    controls: dict[str, Any]
    changed_variable: str
    seed: int
    model_config: dict[str, Any]
    optimizer_config: dict[str, Any]
    schedule_config: dict[str, Any]
    data_config: dict[str, Any]
    runtime_config: dict[str, Any]
    raw_artifacts: list[str]
    derived_metrics: dict[str, Any]
    statistical_summary: dict[str, Any]
    decision: str
    confidence: str
    limitations: list[str]
    reproducibility_command: str
    git_commit_if_available: str
    timestamp: str
    execution_mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LabConfig:
    """Combined config for training experiments."""

    model: ModelConfig = field(default_factory=ModelConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    data: DataConfig = field(default_factory=DataConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    def full_hash(self) -> str:
        from src.core.hashing import config_hash

        return config_hash(
            {
                "model": self.model.to_dict(),
                "optimizer": self.optimizer.to_dict(),
                "schedule": self.schedule.to_dict(),
                "data": self.data.to_dict(),
                "runtime": self.runtime.to_dict(),
            }
        )
