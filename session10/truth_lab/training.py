"""Training loop with gradient-norm logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import torch

from truth_lab.config import LabConfig
from truth_lab.data import TinyCorpus, make_batch
from truth_lab.model import TinyGPT

# Detection thresholds (documented explicitly for reproducibility)
GRAD_BEFORE_LOSS_GRAD_THRESHOLD = 0.15
GRAD_BEFORE_LOSS_LOSS_THRESHOLD = 0.05
GRAD_BEFORE_LOSS_WINDOW = 3
GRAD_SPIKE_FACTOR = 1.5


@dataclass
class StepLog:
    step: int
    loss: float
    grad_norm: float
    learning_rate: float
    update_norm: float


@dataclass
class TrainingHistory:
    steps: List[StepLog] = field(default_factory=list)

    def to_dicts(self) -> List[Dict[str, float]]:
        return [
            {
                "step": s.step,
                "loss": s.loss,
                "grad_norm": s.grad_norm,
                "learning_rate": s.learning_rate,
                "update_norm": s.update_norm,
            }
            for s in self.steps
        ]


def grad_norm(model: TinyGPT) -> float:
    total = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total += float(p.grad.data.norm(2).item() ** 2)
    return total ** 0.5


def parameter_update_norm(before: List[torch.Tensor], after: List[torch.Tensor]) -> float:
    total = 0.0
    for b, a in zip(before, after):
        total += float((a - b).norm(2).item() ** 2)
    return total ** 0.5


def train_steps(
    model: TinyGPT,
    corpus: TinyCorpus,
    cfg: LabConfig,
    n_steps: int,
    batch_size: int = 2,
    seed_offset: int = 0,
) -> TrainingHistory:
    device = torch.device(cfg.device)
    model = model.to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )
    history = TrainingHistory()
    for step in range(n_steps):
        x, y, m = make_batch(corpus, batch_size, cfg.block_size, cfg.seed + seed_offset + step)
        x, y, m = x.to(device), y.to(device), m.to(device)
        model.train()
        weights_before = [p.detach().clone() for p in model.parameters()]
        optimizer.zero_grad(set_to_none=True)
        _, trace = model(x, targets=y, mask=m, trace=True)
        assert trace is not None and trace.loss is not None
        loss = trace.loss
        loss.backward()
        gn = grad_norm(model)
        if cfg.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        lr = optimizer.param_groups[0]["lr"]
        optimizer.step()
        weights_after = [p.detach().clone() for p in model.parameters()]
        un = parameter_update_norm(weights_before, weights_after)
        history.steps.append(
            StepLog(
                step=step,
                loss=float(loss.item()),
                grad_norm=gn,
                learning_rate=lr,
                update_norm=un,
            )
        )
    return history


def find_grad_before_loss(
    history: TrainingHistory,
    grad_threshold: float = GRAD_BEFORE_LOSS_GRAD_THRESHOLD,
    loss_threshold: float = GRAD_BEFORE_LOSS_LOSS_THRESHOLD,
    window: int = GRAD_BEFORE_LOSS_WINDOW,
) -> Optional[Dict[str, float]]:
    """Find earliest step where grad_norm changes significantly before loss does."""
    steps = history.steps
    if len(steps) < window + 1:
        return None

    for i in range(window, len(steps)):
        prev = steps[i - window]
        cur = steps[i]
        grad_change = abs(cur.grad_norm - prev.grad_norm) / max(prev.grad_norm, 1e-8)
        loss_change = abs(cur.loss - prev.loss) / max(prev.loss, 1e-8)
        if grad_change > grad_threshold and loss_change < loss_threshold:
            return {
                "step": float(cur.step),
                "grad_norm": cur.grad_norm,
                "prev_grad_norm": prev.grad_norm,
                "grad_rel_change": grad_change,
                "loss": cur.loss,
                "prev_loss": prev.loss,
                "loss_rel_change": loss_change,
                "learning_rate": cur.learning_rate,
                "update_norm": cur.update_norm,
                "grad_threshold": grad_threshold,
                "loss_threshold": loss_threshold,
                "window": float(window),
            }
    return None


def find_gradient_spike(
    history: TrainingHistory,
    spike_factor: float = GRAD_SPIKE_FACTOR,
) -> Optional[Dict[str, float]]:
    """Find step where grad norm spikes relative to rolling median."""
    norms = [s.grad_norm for s in history.steps]
    losses = [s.loss for s in history.steps]
    if len(norms) < 5:
        return None
    best_i, best_ratio = None, 0.0
    for i in range(2, len(norms) - 2):
        local = sorted(norms[i - 2 : i + 3])
        median = local[len(local) // 2]
        ratio = norms[i] / max(median, 1e-8)
        if ratio > spike_factor and ratio > best_ratio:
            best_ratio = ratio
            best_i = i
    if best_i is None:
        return None
    return {
        "step": float(history.steps[best_i].step),
        "grad_norm": norms[best_i],
        "local_median_grad_norm": sorted(norms[best_i - 2 : best_i + 3])[2],
        "spike_ratio": best_ratio,
        "loss_before": losses[max(0, best_i - 1)],
        "loss_at": losses[best_i],
        "loss_after": losses[min(len(losses) - 1, best_i + 1)],
        "spike_factor_threshold": spike_factor,
    }


def clone_model_state(model: TinyGPT) -> List[torch.Tensor]:
    return [p.detach().clone() for p in model.parameters()]


def models_differ(before: List[torch.Tensor], after: List[torch.Tensor]) -> bool:
    return any(not torch.equal(a, b) for a, b in zip(before, after))
