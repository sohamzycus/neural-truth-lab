"""~20M causal LM baseline."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from src.config import ModelConfig

@dataclass
class ParamBreakdown:
    total: int
    embedding: int
    transformer_blocks: int
    lm_head: int
    other: int
    def to_dict(self) -> dict:
        return self.__dict__.copy()

def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def parameter_breakdown(model: nn.Module) -> ParamBreakdown:
    emb = blocks = head = other = 0
    for name, p in model.named_parameters():
        n = p.numel()
        if "token_emb" in name or "pos_emb" in name: emb += n
        elif "lm_head" in name: head += n
        elif "blocks" in name: blocks += n
        else: other += n
    if getattr(model.cfg, "tie_weights", False):
        head = 0
    return ParamBreakdown(count_parameters(model), emb, blocks, head, other)

def theoretical_param_count(cfg: ModelConfig) -> int:
    d, v, l = cfg.n_embd, cfg.vocab_size, cfg.n_layer
    emb = v * d + cfg.block_size * d
    per_layer = 4 * d * d + 8 * d * d + 4 * d
    ln_f = 2 * d
    head = 0 if cfg.tie_weights else v * d
    return emb + l * per_layer + ln_f + head

class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: ModelConfig, dim: int | None = None) -> None:
        super().__init__()
        self.dim = dim or cfg.n_embd
        assert self.dim % cfg.n_head == 0
        self.n_head = cfg.n_head
        self.head_dim = self.dim // cfg.n_head
        self.qkv = nn.Linear(self.dim, 3 * self.dim, bias=False)
        self.proj = nn.Linear(self.dim, self.dim, bias=False)
        self.register_buffer("mask", torch.tril(torch.ones(cfg.block_size, cfg.block_size)).view(1, 1, cfg.block_size, cfg.block_size))
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, t, c = x.shape
        qkv = self.qkv(x).reshape(b, t, 3, self.n_head, self.head_dim)
        q, k, v = qkv.unbind(dim=2)
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        att = att.masked_fill(self.mask[:, :, :t, :t] == 0, float("-inf"))
        out = (F.softmax(att, dim=-1) @ v).transpose(1, 2).contiguous().view(b, t, c)
        return self.proj(out)

class MLP(nn.Module):
    def __init__(self, dim: int) -> None:
        super().__init__()
        h = 4 * dim
        self.fc1, self.fc2 = nn.Linear(dim, h), nn.Linear(h, dim)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.gelu(self.fc1(x)))

class TransformerBlock(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(cfg.n_embd), nn.LayerNorm(cfg.n_embd)
        self.attn, self.mlp = CausalSelfAttention(cfg), MLP(cfg.n_embd)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))

class CausalLM(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.token_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        if cfg.tie_weights:
            self.lm_head.weight = self.token_emb.weight
    def forward(self, idx: torch.Tensor, targets: Optional[torch.Tensor] = None):
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        x = self.token_emb(idx) + self.pos_emb(pos)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, self.cfg.vocab_size), targets[:, 1:].reshape(-1))
        return logits, loss

def build_model(cfg: ModelConfig, reversible_method: str = "none"):
    from src.reversible import ReversibleCausalLM
    if reversible_method in ("euler", "midpoint"):
        return ReversibleCausalLM(cfg, method=reversible_method)
    return CausalLM(cfg)
