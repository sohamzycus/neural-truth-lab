"""MoE FFN + dense → MoE conversion."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from src.config import ModelConfig
from src.model import CausalSelfAttention, DenseCausalLM, DenseFFN, count_parameters


@dataclass
class RoutingStats:
    expert_utilization: list[float]
    router_entropy: float
    active_experts: list[int]


class ExpertFFN(nn.Module):
    def __init__(self, dim: int, hidden: int) -> None:
        super().__init__()
        self.fc1 = nn.Linear(dim, hidden, bias=False)
        self.fc2 = nn.Linear(hidden, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.gelu(self.fc1(x)))


class MoEFFN(nn.Module):
    """Router → top-k experts → weighted sum."""

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.num_experts = cfg.num_experts
        self.top_k = cfg.top_k
        dim = cfg.n_embd
        h_e = cfg.expert_hidden
        self.experts = nn.ModuleList(
            [ExpertFFN(dim, h_e) for _ in range(cfg.num_experts)]
        )
        self.router = nn.Linear(dim, cfg.num_experts, bias=False)
        nn.init.zeros_(self.router.weight)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, RoutingStats]:
        b, t, c = x.shape
        flat = x.reshape(-1, c)
        n = flat.shape[0]
        logits = self.router(flat)
        probs = F.softmax(logits, dim=-1)
        top_w, top_idx = torch.topk(probs, self.top_k, dim=-1)
        top_w = top_w / top_w.sum(dim=-1, keepdim=True).clamp(min=1e-9)

        out = torch.zeros_like(flat)
        for k in range(self.top_k):
            w_k = top_w[:, k]
            idx_k = top_idx[:, k]
            for e in range(self.num_experts):
                mask = idx_k == e
                if not mask.any():
                    continue
                out[mask] += w_k[mask].unsqueeze(-1) * self.experts[e](flat[mask])

        util = torch.zeros(self.num_experts, device=x.device)
        for k in range(self.top_k):
            util += torch.bincount(top_idx[:, k], minlength=self.num_experts).float()
        util = (util / (n * self.top_k)).tolist()
        entropy = -(probs * (probs + 1e-9).log()).sum(dim=-1).mean().item()
        active = sorted({int(i) for i in top_idx.reshape(-1).tolist()})

        return out.view(b, t, c), RoutingStats(util, entropy, active)


def init_experts_from_dense_ffn(dense: DenseFFN, cfg: ModelConfig) -> MoEFFN:
    """Partition dense FFN along the intermediate axis into expert slices."""
    dim = dense.fc1.in_features
    h = dense.fc1.out_features
    num_experts = cfg.num_experts
    if h % num_experts:
        raise ValueError("dense hidden size must divide num_experts")
    h_e = h // num_experts
    assert h_e == cfg.expert_hidden
    moe = MoEFFN(cfg)
    for i, expert in enumerate(moe.experts):
        sl = slice(i * h_e, (i + 1) * h_e)
        expert.fc1.weight.data.copy_(dense.fc1.weight.data[sl, :])
        expert.fc2.weight.data.copy_(dense.fc2.weight.data[:, sl])
    return moe


class MoETransformerBlock(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.n_embd)
        self.ln2 = nn.LayerNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.mlp = MoEFFN(cfg)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, RoutingStats]:
        x = x + self.attn(self.ln1(x))
        mlp_out, stats = self.mlp(self.ln2(x))
        return x + mlp_out, stats


class MoECausalLM(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.token_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([MoETransformerBlock(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        if cfg.tie_weights:
            self.lm_head.weight = self.token_emb.weight
        self.last_routing: list[RoutingStats] = []

    def forward(
        self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        x = self.token_emb(idx) + self.pos_emb(pos)
        self.last_routing = []
        for block in self.blocks:
            x, stats = block(x)
            self.last_routing.append(stats)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits[:, :-1].reshape(-1, self.cfg.vocab_size),
                targets[:, 1:].reshape(-1),
            )
        return logits, loss


@torch.no_grad()
def conversion_fidelity(
    dense: DenseCausalLM,
    moe: MoECausalLM,
    probe_x: torch.Tensor,
    probe_y: torch.Tensor,
) -> dict[str, float]:
    """Same probe batch before/after conversion (architecture change, not re-init)."""
    dense.eval()
    moe.eval()
    d_logits, d_loss = dense(probe_x, targets=probe_y)
    m_logits, m_loss = moe(probe_x, targets=probe_y)
    assert d_logits is not None and m_logits is not None
    assert d_loss is not None and m_loss is not None
    mse = F.mse_loss(d_logits, m_logits).item()
    return {
        "dense_output_loss": float(d_loss.item()),
        "converted_moe_output_loss": float(m_loss.item()),
        "logits_mse": float(mse),
        "loss_delta_moe_minus_dense": float(m_loss.item() - d_loss.item()),
    }


def convert_dense_to_moe(dense: DenseCausalLM, cfg: ModelConfig) -> MoECausalLM:
    """Copy trained dense weights; replace each dense FFN with partitioned MoE experts."""
    moe = MoECausalLM(cfg)
    dense_sd = dense.state_dict()
    moe_sd = moe.state_dict()
    skip_prefixes = ("blocks.",)
    for key, val in dense_sd.items():
        if key.startswith("blocks.") and ".mlp." in key:
            continue
        if key in moe_sd and moe_sd[key].shape == val.shape:
            moe_sd[key] = val
    moe.load_state_dict(moe_sd, strict=False)

    for i in range(cfg.n_layer):
        dense_ffn = dense.blocks[i].mlp
        moe.blocks[i].mlp = init_experts_from_dense_ffn(dense_ffn, cfg)
    return moe
