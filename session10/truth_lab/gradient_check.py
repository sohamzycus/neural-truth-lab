"""Finite-difference gradient verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import torch
import numpy as np

from truth_lab.model import TinyGPT


@dataclass
class GradientCheckResult:
    param_name: str
    index: Tuple[int, ...]
    w: float
    epsilon: float
    loss_at_w: float
    loss_at_w_plus: float
    loss_at_w_minus: float
    finite_diff: float
    autograd: float
    abs_diff: float
    rel_diff: float
    verdict: str


def _scalar_loss(
    model: TinyGPT,
    input_ids: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
) -> float:
    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    return float(trace.loss.item())


def verify_gradient(
    model: TinyGPT,
    input_ids: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
    param_name: str | None = None,
    index: Tuple[int, ...] | None = None,
    epsilon: float = 1e-4,
    rel_tol: float = 5e-3,
) -> GradientCheckResult:
    """Compare autograd vs central finite difference on one scalar parameter."""
    model.eval()
    named = dict(model.named_parameters())

    # ponytail: pick a parameter with non-zero gradient so the check is meaningful
    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    trace.loss.backward()
    if param_name is None or index is None:
        best_name, best_idx, best_mag = None, None, 0.0
        for name, p in named.items():
            if p.grad is None:
                continue
            flat = p.grad.abs().view(-1)
            val, pos = flat.max(dim=0)
            if float(val) > best_mag:
                best_mag = float(val)
                best_name = name
                best_idx = tuple(np.unravel_index(int(pos), tuple(p.grad.shape)))
        param_name = best_name or next(iter(named))
        index = best_idx or (0,)
    param = named[param_name]
    original = param.data[index].clone()
    w = float(original.item())

    loss_at_w = _scalar_loss(model, input_ids, targets, mask)
    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    trace.loss.backward()
    autograd = float(param.grad[index].item())

    param.data[index] = w + epsilon
    loss_plus = _scalar_loss(model, input_ids, targets, mask)
    param.data[index] = w - epsilon
    loss_minus = _scalar_loss(model, input_ids, targets, mask)
    param.data[index] = original

    finite = (loss_plus - loss_minus) / (2 * epsilon)
    abs_diff = abs(finite - autograd)
    denom = max(abs(autograd), abs(finite), 1e-12)
    rel_diff = abs_diff / denom
    verdict = "PASS" if rel_diff < rel_tol else "INVESTIGATE"

    model.zero_grad(set_to_none=True)
    return GradientCheckResult(
        param_name=param_name,
        index=index,
        w=w,
        epsilon=epsilon,
        loss_at_w=loss_at_w,
        loss_at_w_plus=loss_plus,
        loss_at_w_minus=loss_minus,
        finite_diff=finite,
        autograd=autograd,
        abs_diff=abs_diff,
        rel_diff=rel_diff,
        verdict=verdict,
    )
