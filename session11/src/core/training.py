"""Shared training loop with schedule and layer ratio hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import torch
import torch.nn as nn

from src.core.data import TinyCorpus, make_batch
from src.core.model import TinyGPT
from src.core.schemas import LabConfig
from src.core.seed import set_seed
from src.schedules import SCHEDULES


@dataclass
class StepLog:
    step: int
    loss: float
    grad_norm: float
    learning_rate: float
    update_norm: float


@dataclass
class LayerRatioLog:
    layer_name: str
    parameter_shape: list
    parameter_norm: float
    gradient_norm: float
    update_norm: float
    update_to_weight_ratio: float
    learning_rate: float
    warmup_fraction: float
    schedule_multiplier: float
    optimizer_step: int


@dataclass
class TrainingResult:
    steps: List[StepLog] = field(default_factory=list)
    layer_ratios: List[LayerRatioLog] = field(default_factory=list)
    divergence_flag: bool = False
    nan_flag: bool = False


def _grad_norm(model: nn.Module) -> float:
    total = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total += float(p.grad.data.norm(2).item() ** 2)
    return total ** 0.5


def _param_delta_norm(before: dict, after: dict, name: str) -> float:
    return float((after[name] - before[name]).norm(2).item())


def train_with_schedule(
    cfg: LabConfig,
    corpus: TinyCorpus,
    n_steps: int,
    schedule_name: str = "wsd",
    log_layer_ratios: bool = False,
    init_state: Optional[dict[str, torch.Tensor]] = None,
) -> TrainingResult:
    set_seed(cfg.model.seed)
    device = torch.device(cfg.runtime.device)
    model = TinyGPT(cfg.model, corpus.vocab_size).to(device)
    if init_state:
        model.load_state_dict(init_state)

    schedule_mod = SCHEDULES[schedule_name]
    base_lr = cfg.optimizer.learning_rate
    opt = torch.optim.AdamW(
        model.parameters(),
        lr=base_lr,
        betas=(cfg.optimizer.beta1, cfg.optimizer.beta2),
        eps=cfg.optimizer.epsilon,
        weight_decay=cfg.optimizer.weight_decay,
    )

    result = TrainingResult()
    cfg.schedule.total_steps = n_steps

    for step in range(n_steps):
        mult = schedule_mod.lr_multiplier(step, cfg.schedule)
        wf = schedule_mod.warmup_fraction(step, cfg.schedule)
        for pg in opt.param_groups:
            pg["lr"] = base_lr * mult

        x, y, m = make_batch(
            corpus, cfg.data.batch_size, cfg.model.block_size,
            cfg.model.seed + cfg.data.seed_offset + step,
        )
        x, y, m = x.to(device), y.to(device), m.to(device)

        before = {n: p.detach().clone() for n, p in model.named_parameters()}
        opt.zero_grad(set_to_none=True)
        _, loss = model(x, targets=y, mask=m)
        if loss is None:
            continue
        loss_val = float(loss.item())
        if loss_val != loss_val:
            result.nan_flag = True
        loss.backward()
        gn = _grad_norm(model)
        if cfg.runtime.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.runtime.grad_clip)

        lr = opt.param_groups[0]["lr"]
        opt.step()
        after = {n: p.detach().clone() for n, p in model.named_parameters()}

        total_update = sum((after[n] - before[n]).norm(2).item() ** 2 for n in before) ** 0.5
        result.steps.append(StepLog(step, loss_val, gn, lr, total_update))

        if log_layer_ratios:
            from src.metrics.ratio_metrics import update_to_weight_ratio
            for name, param in model.named_parameters():
                if not param.requires_grad:
                    continue
                pn = float(before[name].norm(2).item())
                gn_l = float(param.grad.norm(2).item()) if param.grad is not None else 0.0
                un = _param_delta_norm(before, after, name)
                result.layer_ratios.append(
                    LayerRatioLog(
                        layer_name=name,
                        parameter_shape=list(param.shape),
                        parameter_norm=pn,
                        gradient_norm=gn_l,
                        update_norm=un,
                        update_to_weight_ratio=update_to_weight_ratio(un, pn),
                        learning_rate=lr,
                        warmup_fraction=wf,
                        schedule_multiplier=mult,
                        optimizer_step=step,
                    )
                )

        if loss_val > 100 or loss_val != loss_val:
            result.divergence_flag = True

    return result


def capture_init_state(model: TinyGPT) -> dict[str, torch.Tensor]:
    return {k: v.detach().clone() for k, v in model.state_dict().items()}


def fresh_model_with_state(cfg: LabConfig, corpus: TinyCorpus, state: dict) -> TinyGPT:
    set_seed(cfg.model.seed)
    model = TinyGPT(cfg.model, corpus.vocab_size)
    model.load_state_dict(state)
    return model
