"""Tiny causal language model with tensor tracing hooks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from truth_lab.config import LabConfig


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: LabConfig) -> None:
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0
        self.n_head = cfg.n_head
        self.head_dim = cfg.n_embd // cfg.n_head
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=False)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=False)
        self.register_buffer(
            "mask",
            torch.tril(torch.ones(cfg.block_size, cfg.block_size)).view(
                1, 1, cfg.block_size, cfg.block_size
            ),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        b, t, c = x.shape
        qkv = self.qkv(x).reshape(b, t, 3, self.n_head, self.head_dim)
        q, k, v = qkv.unbind(dim=2)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        att = att.masked_fill(self.mask[:, :, :t, :t] == 0, float("-inf"))
        att_weights = F.softmax(att, dim=-1)
        att_out = att_weights @ v
        att_out = att_out.transpose(1, 2).contiguous().view(b, t, c)
        out = self.proj(att_out)
        return out, att_weights


class MLP(nn.Module):
    def __init__(self, cfg: LabConfig) -> None:
        super().__init__()
        hidden = 4 * cfg.n_embd
        self.fc1 = nn.Linear(cfg.n_embd, hidden)
        self.fc2 = nn.Linear(hidden, cfg.n_embd)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.gelu(self.fc1(x)))


class TransformerBlock(nn.Module):
    def __init__(self, cfg: LabConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.n_embd)
        self.mlp = MLP(cfg)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        attn_out, att_weights = self.attn(self.ln1(x))
        x = x + attn_out
        mlp_out = self.mlp(self.ln2(x))
        x = x + mlp_out
        return x, attn_out, mlp_out


@dataclass
class TensorTrace:
    input_ids: Optional[torch.Tensor] = None
    embeddings: Optional[torch.Tensor] = None
    hidden_states: list[torch.Tensor] = field(default_factory=list)
    attention_outputs: list[torch.Tensor] = field(default_factory=list)
    mlp_outputs: list[torch.Tensor] = field(default_factory=list)
    final_hidden: Optional[torch.Tensor] = None
    logits: Optional[torch.Tensor] = None
    shifted_logits: Optional[torch.Tensor] = None
    targets: Optional[torch.Tensor] = None
    loss: Optional[torch.Tensor] = None
    mask: Optional[torch.Tensor] = None

    def as_dict(self) -> Dict[str, torch.Tensor]:
        out: Dict[str, torch.Tensor] = {}
        for name in (
            "input_ids",
            "embeddings",
            "final_hidden",
            "logits",
            "shifted_logits",
            "targets",
            "loss",
            "mask",
        ):
            val = getattr(self, name)
            if val is not None:
                out[name] = val
        if self.hidden_states:
            out["hidden_states_layer0"] = self.hidden_states[0]
        if self.attention_outputs:
            out["attention_output_layer0"] = self.attention_outputs[0]
        if self.mlp_outputs:
            out["mlp_output_layer0"] = self.mlp_outputs[0]
        return out


class TinyGPT(nn.Module):
    def __init__(self, cfg: LabConfig, vocab_size: int) -> None:
        super().__init__()
        self.cfg = cfg
        self.vocab_size = vocab_size
        self.token_emb = nn.Embedding(vocab_size, cfg.n_embd)
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd)
        self.lm_head = nn.Linear(cfg.n_embd, vocab_size, bias=False)

    def forward(
        self,
        idx: torch.Tensor,
        targets: Optional[torch.Tensor] = None,
        mask: Optional[torch.Tensor] = None,
        trace: bool = False,
    ) -> tuple[torch.Tensor, TensorTrace | None]:
        b, t = idx.shape
        pos = torch.arange(t, device=idx.device)
        x = self.token_emb(idx) + self.pos_emb(pos)
        tt = TensorTrace(input_ids=idx) if trace else None
        if trace:
            tt.embeddings = x.detach()

        att_cache: list[torch.Tensor] = []
        mlp_cache: list[torch.Tensor] = []
        h_cache: list[torch.Tensor] = []
        for block in self.blocks:
            x, attn_out, mlp_out = block(x)
            if trace:
                h_cache.append(x.detach())
                att_cache.append(attn_out.detach())
                mlp_cache.append(mlp_out.detach())
        x = self.ln_f(x)
        logits = self.lm_head(x)

        if trace:
            tt.hidden_states = h_cache
            tt.attention_outputs = att_cache
            tt.mlp_outputs = mlp_cache
            tt.final_hidden = x.detach()
            tt.logits = logits.detach()

        loss = None
        if targets is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_targets = targets[:, 1:].contiguous()
            if trace:
                tt.shifted_logits = shift_logits.detach()
                tt.targets = shift_targets.detach()
                tt.mask = mask[:, 1:].contiguous().detach() if mask is not None else None
            flat_logits = shift_logits.view(-1, self.vocab_size)
            flat_targets = shift_targets.view(-1)
            if mask is not None:
                flat_mask = mask[:, 1:].reshape(-1)
                if flat_mask.any():
                    loss = F.cross_entropy(flat_logits[flat_mask], flat_targets[flat_mask])
                else:
                    loss = flat_logits.sum() * 0.0
            else:
                loss = F.cross_entropy(flat_logits, flat_targets)
            if trace:
                tt.loss = loss

        return logits, tt

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())
