"""Parameter accounting for dense vs MoE (no bias in FFN; router separate from experts)."""
from __future__ import annotations

from typing import Any

import torch.nn as nn

from src.config import ModelConfig
from src.model import DenseCausalLM, count_parameters
from src.moe import MoECausalLM


def _count_named(model: nn.Module, predicate) -> int:
    return sum(p.numel() for n, p in model.named_parameters() if predicate(n))


def dense_ffn_parameter_count(cfg: ModelConfig) -> int:
    d, h = cfg.n_embd, cfg.ffn_hidden
    per_layer = d * h + h * d
    return per_layer * cfg.n_layer


def moe_expert_parameter_count(cfg: ModelConfig) -> int:
    d, h_e = cfg.n_embd, cfg.expert_hidden
    per_expert = d * h_e + h_e * d
    return per_expert * cfg.num_experts * cfg.n_layer


def router_parameter_count(cfg: ModelConfig) -> int:
    return cfg.n_embd * cfg.num_experts * cfg.n_layer


def active_expert_parameters_per_token(cfg: ModelConfig) -> int:
    d, h_e = cfg.n_embd, cfg.expert_hidden
    per_expert = d * h_e + h_e * d
    return per_expert * cfg.top_k * cfg.n_layer


def active_router_parameters_per_token(cfg: ModelConfig) -> int:
    return cfg.n_embd * cfg.num_experts * cfg.n_layer


def parameter_accounting(dense: DenseCausalLM, moe: MoECausalLM, cfg: ModelConfig) -> dict[str, Any]:
    dense_total = count_parameters(dense)
    moe_total = count_parameters(moe)

    dense_ffn = _count_named(dense, lambda n: ".mlp." in n)
    moe_experts = _count_named(moe, lambda n: ".experts." in n)
    moe_routers = _count_named(moe, lambda n: ".router." in n)

    theory_dense_ffn = dense_ffn_parameter_count(cfg)
    theory_moe_experts = moe_expert_parameter_count(cfg)
    theory_routers = router_parameter_count(cfg)

    active_expert = active_expert_parameters_per_token(cfg)
    active_router = active_router_parameters_per_token(cfg)

    return {
        "dense_total_parameters": dense_total,
        "moe_total_parameters": moe_total,
        "dense_ffn_parameters": dense_ffn,
        "dense_ffn_parameters_theory": theory_dense_ffn,
        "moe_total_expert_parameters": moe_experts,
        "moe_total_expert_parameters_theory": theory_moe_experts,
        "router_parameters_total": moe_routers,
        "router_parameters_per_layer": theory_routers // cfg.n_layer,
        "active_expert_parameters_per_token": active_expert,
        "active_router_parameters_per_token": active_router,
        "active_parameters_per_token_total": active_expert + active_router,
    }
