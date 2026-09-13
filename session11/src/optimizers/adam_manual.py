"""Manual scalar Adam — EXP-ADAM-001, independent of PyTorch calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class AdamManualStep:
    step: int
    gradient: float
    m_t: float
    v_t: float
    m_hat_t: float
    v_hat_t: float
    signed_step: float
    updated_weight: float


def adam_manual_steps(
    initial_weight: float,
    gradients: List[float],
    learning_rate: float = 0.001,
    beta1: float = 0.9,
    beta2: float = 0.999,
    epsilon: float = 1e-8,
    weight_decay: float = 0.0,
    bias_correction: bool = True,
) -> List[AdamManualStep]:
    """Pure Python Adam — no PyTorch used for manual values."""
    w = initial_weight
    m, v = 0.0, 0.0
    rows: List[AdamManualStep] = []
    for t, g in enumerate(gradients, start=1):
        if weight_decay != 0:
            g = g + weight_decay * w
        m = beta1 * m + (1 - beta1) * g
        v = beta2 * v + (1 - beta2) * (g * g)
        if bias_correction:
            m_hat = m / (1 - beta1 ** t)
            v_hat = v / (1 - beta2 ** t)
        else:
            m_hat = m
            v_hat = v
        signed_step = learning_rate * m_hat / ((v_hat ** 0.5) + epsilon)
        w = w - signed_step
        rows.append(
            AdamManualStep(
                step=t,
                gradient=g if weight_decay == 0 else g,
                m_t=m,
                v_t=v,
                m_hat_t=m_hat,
                v_hat_t=v_hat,
                signed_step=signed_step,
                updated_weight=w,
            )
        )
    return rows
