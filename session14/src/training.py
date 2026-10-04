"""Training loops for dense and MoE phases."""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn

from src.config import ExperimentConfig
from src.data import CorpusSplit, make_eval_batch, make_train_batch
from src.moe import MoECausalLM
from src.seed import set_seed


def resolve_device(name: str) -> torch.device:
    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(name)


def lr_at_step(base: float, step: int, warmup: int) -> float:
    if warmup <= 0:
        return base
    return base * min(1.0, (step + 1) / warmup)


@torch.no_grad()
def eval_heldout_loss(
    model: nn.Module,
    split: CorpusSplit,
    cfg: ExperimentConfig,
    device: torch.device,
    batch_seed: int,
) -> float:
    model.eval()
    x, y = make_eval_batch(
        split, cfg.training.batch_size, cfg.model.block_size, batch_seed
    )
    x, y = x.to(device), y.to(device)
    _, loss = model(x, targets=y)
    return float(loss.item())


def _aggregate_routing(model: MoECausalLM) -> dict[str, Any]:
    if not model.last_routing:
        return {}
    n_exp = model.cfg.num_experts
    util = [0.0] * n_exp
    ent = 0.0
    active: set[int] = set()
    for st in model.last_routing:
        for i, u in enumerate(st.expert_utilization):
            util[i] += u
        ent += st.router_entropy
        active.update(st.active_experts)
    k = len(model.last_routing)
    util = [u / k for u in util]
    return {
        "expert_utilization": util,
        "router_entropy": ent / k,
        "active_experts": sorted(active),
        "top_k": model.cfg.top_k,
    }


def capture_routing_on_batch(
    model: MoECausalLM,
    split: CorpusSplit,
    cfg: ExperimentConfig,
    device: torch.device,
    seed: int,
    train: bool,
) -> dict[str, Any]:
    model.train()
    if train:
        x, y = make_train_batch(
            split, cfg.training.batch_size, cfg.model.block_size, seed
        )
    else:
        x, y = make_eval_batch(
            split, cfg.training.batch_size, cfg.model.block_size, seed
        )
    x = x.to(device)
    model(x)
    return _aggregate_routing(model)


def train_phase(
    model: nn.Module,
    cfg: ExperimentConfig,
    split: CorpusSplit,
    device: torch.device,
    steps: int,
    log_path: Path,
    phase: str,
    start_step: int = 0,
    tokens_offset: int = 0,
) -> dict[str, Any]:
    model.train()
    opt = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.training.learning_rate,
        weight_decay=cfg.training.weight_decay,
    )
    seq = cfg.model.block_size
    t0 = time.perf_counter()
    tokens_seen = tokens_offset
    rows: list[dict[str, Any]] = []

    log_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "phase",
        "step",
        "loss",
        "learning_rate",
        "tokens_seen",
        "elapsed_seconds",
        "expert_utilization",
        "active_experts",
        "top_k",
        "router_entropy",
    ]

    for step in range(steps):
        lr = lr_at_step(cfg.training.learning_rate, step, cfg.training.warmup_steps)
        for pg in opt.param_groups:
            pg["lr"] = lr
        seed = cfg.seed + start_step + step
        x, y = make_train_batch(split, cfg.training.batch_size, seq, seed)
        x, y = x.to(device), y.to(device)
        opt.zero_grad(set_to_none=True)
        _, loss = model(x, targets=y)
        lv = float(loss.item())
        loss.backward()
        if cfg.training.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.training.grad_clip)
        opt.step()
        tokens_seen += cfg.training.batch_size * seq

        route: dict[str, Any] = {}
        if isinstance(model, MoECausalLM):
            route = _aggregate_routing(model)

        elapsed = time.perf_counter() - t0
        if step % cfg.training.log_every == 0 or step == steps - 1:
            rows.append(
                {
                    "phase": phase,
                    "step": start_step + step,
                    "loss": lv,
                    "learning_rate": lr,
                    "tokens_seen": tokens_seen,
                    "elapsed_seconds": round(elapsed, 4),
                    "expert_utilization": json.dumps(route.get("expert_utilization", [])),
                    "active_experts": json.dumps(route.get("active_experts", [])),
                    "top_k": route.get("top_k", ""),
                    "router_entropy": route.get("router_entropy", ""),
                }
            )

    final_loss = rows[-1]["loss"] if rows else float("nan")

    with log_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    return {
        "final_batch_loss": final_loss,
        "tokens_seen": tokens_seen,
        "elapsed_seconds": time.perf_counter() - t0,
        "rows": rows,
    }
