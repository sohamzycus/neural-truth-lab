"""Gradient accumulation: naive vs token-weighted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import torch
import torch.nn.functional as F

from truth_lab.model import TinyGPT


@dataclass
class AccumulationLosses:
    loss_a: float
    loss_b: float
    tokens_a: int
    tokens_b: int
    naive: float
    correct: float


def per_token_loss(
    model: TinyGPT,
    x: torch.Tensor,
    y: torch.Tensor,
    mask: torch.Tensor,
) -> Tuple[float, int]:
    model.eval()
    with torch.no_grad():
        logits, _ = model(x, targets=None)
    shift_logits = logits[:, :-1, :].contiguous()
    shift_targets = y[:, 1:].contiguous()
    shift_mask = mask[:, 1:].contiguous()
    flat_logits = shift_logits.view(-1, model.vocab_size)
    flat_targets = shift_targets.reshape(-1)
    flat_mask = shift_mask.reshape(-1)
    n = int(flat_mask.sum().item())
    if n == 0:
        return 0.0, 0
    ce = F.cross_entropy(flat_logits[flat_mask], flat_targets[flat_mask], reduction="none")
    return float(ce.mean().item()), n


def combine_accumulation(loss_a: float, n_a: int, loss_b: float, n_b: int) -> AccumulationLosses:
    naive = (loss_a + loss_b) / 2
    correct = (loss_a * n_a + loss_b * n_b) / (n_a + n_b)
    return AccumulationLosses(
        loss_a=loss_a,
        loss_b=loss_b,
        tokens_a=n_a,
        tokens_b=n_b,
        naive=naive,
        correct=correct,
    )


def train_accumulation_step(
    model: TinyGPT,
    optimizer: torch.optim.Optimizer,
    microbatches: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    mode: str,
) -> float:
    """One optimizer step. mode is 'naive' or 'correct'."""
    model.train()
    optimizer.zero_grad(set_to_none=True)

    losses: List[Tuple[torch.Tensor, int]] = []
    for x, y, m in microbatches:
        _, trace = model(x, targets=y, mask=m, trace=True)
        assert trace is not None and trace.loss is not None
        n = int(m[:, 1:].sum().item())
        losses.append((trace.loss, n))

    if mode == "naive":
        for loss, _ in losses:
            (loss / len(losses)).backward()
        reported = sum(float(l.item()) for l, _ in losses) / len(losses)
    elif mode == "correct":
        total_tokens = sum(n for _, n in losses)
        for loss, n in losses:
            (loss * (n / total_tokens)).backward()
        reported = sum(float(l.item()) * n for l, n in losses) / total_tokens
    else:
        raise ValueError(f"unknown mode: {mode}")

    optimizer.step()
    return reported
