"""Finite-difference gradient verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np
import torch

from truth_lab.model import TinyGPT

DEFAULT_EPSILONS = (1e-2, 1e-3, 1e-4, 1e-5, 1e-6)


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


@dataclass
class EpsilonSweepRow:
    epsilon: float
    finite_diff: float
    autograd: float
    abs_error: float
    rel_error: float


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


def _pick_param_with_gradient(model: TinyGPT, named: dict[str, torch.Tensor]) -> Tuple[str, Tuple[int, ...]]:
    best_name, best_idx, best_mag = None, (0,), 0.0
    for name, p in named.items():
        if p.grad is None:
            continue
        flat = p.grad.abs().view(-1)
        val, pos = flat.max(dim=0)
        if float(val) > best_mag:
            best_mag = float(val)
            best_name = name
            best_idx = tuple(np.unravel_index(int(pos), tuple(p.grad.shape)))
    return best_name or next(iter(named)), best_idx


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

    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    trace.loss.backward()
    if param_name is None or index is None:
        param_name, index = _pick_param_with_gradient(model, named)
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


def gradient_epsilon_sweep(
    model: TinyGPT,
    input_ids: torch.Tensor,
    targets: torch.Tensor,
    mask: torch.Tensor,
    param_name: str | None = None,
    index: Tuple[int, ...] | None = None,
    epsilons: Sequence[float] = DEFAULT_EPSILONS,
) -> Tuple[List[EpsilonSweepRow], str, Tuple[int, ...], float]:
    """Sweep epsilon values; return rows and the fixed parameter location."""
    model.eval()
    named = dict(model.named_parameters())
    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    trace.loss.backward()
    if param_name is None or index is None:
        param_name, index = _pick_param_with_gradient(model, named)
    param = named[param_name]
    original = param.data[index].clone()
    w = float(original.item())

    model.zero_grad(set_to_none=True)
    _, trace = model(input_ids, targets=targets, mask=mask, trace=True)
    assert trace is not None and trace.loss is not None
    trace.loss.backward()
    autograd = float(param.grad[index].item())

    rows: List[EpsilonSweepRow] = []
    for eps in epsilons:
        param.data[index] = w + eps
        loss_plus = _scalar_loss(model, input_ids, targets, mask)
        param.data[index] = w - eps
        loss_minus = _scalar_loss(model, input_ids, targets, mask)
        finite = (loss_plus - loss_minus) / (2 * eps)
        abs_err = abs(finite - autograd)
        rel_err = abs_err / max(abs(autograd), abs(finite), 1e-12)
        rows.append(EpsilonSweepRow(eps, finite, autograd, abs_err, rel_err))

    param.data[index] = original
    model.zero_grad(set_to_none=True)
    return rows, param_name, index, autograd


def pick_best_epsilon(rows: Sequence[EpsilonSweepRow]) -> EpsilonSweepRow:
    """Pick epsilon with smallest relative error (numerically justified choice)."""
    return min(rows, key=lambda r: r.rel_error)


def format_sweep_table(rows: Sequence[EpsilonSweepRow]) -> str:
    lines = [
        "| epsilon | finite difference | autograd | abs error | relative error |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        lines.append(
            f"| {r.epsilon:.0e} | {r.finite_diff:.8g} | {r.autograd:.8g} "
            f"| {r.abs_error:.3e} | {r.rel_error:.3e} |"
        )
    return "\n".join(lines)
