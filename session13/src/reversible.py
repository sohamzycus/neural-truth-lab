"""Reversible transformer blocks (RevNet-style) with Euler and Midpoint variants."""
from __future__ import annotations
import math
from typing import Literal, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from src.config import ModelConfig
from src.model import CausalSelfAttention, MLP, CausalLM, count_parameters

Method = Literal["euler", "midpoint"]

class RevFunctions(nn.Module):
    def __init__(self, cfg: ModelConfig, half: int) -> None:
        super().__init__()
        self.ln_f = nn.LayerNorm(half)
        self.ln_g = nn.LayerNorm(half)
        mini = ModelConfig(**{**cfg.__dict__, "n_embd": half})
        self.f_attn = CausalSelfAttention(mini, dim=half)
        self.g_mlp = MLP(half)

    def F(self, x2: torch.Tensor) -> torch.Tensor:
        return self.f_attn(self.ln_f(x2))

    def G(self, x: torch.Tensor) -> torch.Tensor:
        return self.g_mlp(self.ln_g(x))

class ReversibleBlock(nn.Module):
    def __init__(self, cfg: ModelConfig, method: Method = "euler") -> None:
        super().__init__()
        assert cfg.n_embd % 2 == 0
        self.method = method
        self.half = cfg.n_embd // 2
        self.ops = RevFunctions(cfg, self.half)

    def forward_step(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        f = self.ops.F(x2)
        y1 = x1 + f
        if self.method == "euler":
            g = self.ops.G(y1)
        else:
            g = self.ops.G(x1 + 0.5 * f)
        y2 = x2 + g
        return y1, y2

    def inverse_step(self, y1: torch.Tensor, y2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        g = self.ops.G(y1)
        x2 = y2 - g
        f = self.ops.F(x2)
        x1 = y1 - f
        return x1, x2

    def reconstruction_error(self, x1: torch.Tensor, x2: torch.Tensor) -> float:
        y1, y2 = self.forward_step(x1, x2)
        rx1, rx2 = self.inverse_step(y1, y2)
        return float((rx1 - x1).abs().max().item() + (rx2 - x2).abs().max().item())

class ReversibleBlockFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x1, x2, block: ReversibleBlock):
        ctx.block = block
        with torch.no_grad():
            y1, y2 = block.forward_step(x1, x2)
        ctx.save_for_backward(y1.detach(), y2.detach())
        return y1, y2

    @staticmethod
    def backward(ctx, dy1, dy2):
        block = ctx.block
        y1, y2 = ctx.saved_tensors
        with torch.enable_grad():
            y1g, y2g = y1.detach().requires_grad_(True), y2.detach().requires_grad_(True)
            x2 = y2g - block.ops.G(y1g)
            x1 = y1g - block.ops.F(x2)
            x1.retain_grad(); x2.retain_grad()
            y1n, y2n = block.forward_step(x1, x2)
            torch.autograd.backward((y1n, y2n), (dy1, dy2))
        return x1.grad, x2.grad, None

def apply_reversible_block(x1, x2, block: ReversibleBlock):
    return ReversibleBlockFn.apply(x1, x2, block)

def reversible_depth_for_param_parity(cfg: ModelConfig) -> int:
    target = count_parameters(CausalLM(cfg))
    n = cfg.n_layer
    while n <= 64:
        m = ReversibleCausalLM(cfg, method="euler", n_blocks=n)
        if count_parameters(m) >= target * 0.97:
            return n
        n += 1
    return n

class ReversibleCausalLM(nn.Module):
    def __init__(self, cfg: ModelConfig, method: Method = "euler", n_blocks: int | None = None) -> None:
        super().__init__()
        self.cfg = cfg
        self.method = method
        depth = n_blocks or reversible_depth_for_param_parity(cfg)
        self.n_rev_blocks = depth
        self.token_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([ReversibleBlock(cfg, method) for _ in range(depth)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        if cfg.tie_weights:
            self.lm_head.weight = self.token_emb.weight

    def _split(self, x: torch.Tensor):
        return x[..., : self.cfg.n_embd // 2], x[..., self.cfg.n_embd // 2 :]

    def _merge(self, x1, x2):
        return torch.cat([x1, x2], dim=-1)

    def forward(self, idx: torch.Tensor, targets=None):
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        x = self.token_emb(idx) + self.pos_emb(pos)
        x1, x2 = self._split(x)
        for block in self.blocks:
            if self.training:
                x1, x2 = apply_reversible_block(x1, x2, block)
            else:
                x1, x2 = block.forward_step(x1, x2)
        x = self.ln_f(self._merge(x1, x2))
        logits = self.lm_head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, self.cfg.vocab_size), targets[:, 1:].reshape(-1))
        return logits, loss
