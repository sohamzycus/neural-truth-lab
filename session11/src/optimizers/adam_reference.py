"""PyTorch Adam reference — EXP-ADAM-001 comparison only."""

from __future__ import annotations

from typing import List

import torch


def adam_pytorch_steps(
    initial_weight: float,
    gradients: List[float],
    learning_rate: float = 0.001,
    beta1: float = 0.9,
    beta2: float = 0.999,
    epsilon: float = 1e-8,
    weight_decay: float = 0.0,
    bias_correction: bool = True,
) -> List[dict]:
    w = torch.tensor(initial_weight, dtype=torch.float64, requires_grad=False)
    param = torch.nn.Parameter(w.clone())
    opt = torch.optim.Adam(
        [param],
        lr=learning_rate,
        betas=(beta1, beta2),
        eps=epsilon,
        weight_decay=weight_decay,
    )
    # ponytail: PyTorch Adam always uses bias correction; for no-bias we use manual
    if not bias_correction:
        raise ValueError("Use adam_manual for bias_correction=False")

    rows = []
    for t, g in enumerate(gradients, start=1):
        opt.zero_grad()
        param.grad = torch.tensor(g, dtype=torch.float64)
        state = opt.state[param]
        opt.step()
        m = state["exp_avg"].item()
        v = state["exp_avg_sq"].item()
        m_hat = m / (1 - beta1 ** t)
        v_hat = v / (1 - beta2 ** t)
        signed_step = learning_rate * m_hat / ((v_hat ** 0.5) + epsilon)
        rows.append(
            {
                "step": t,
                "gradient": g,
                "m_t": m,
                "v_t": v,
                "m_hat_t": m_hat,
                "v_hat_t": v_hat,
                "signed_step": signed_step,
                "updated_weight": param.item(),
            }
        )
    return rows
