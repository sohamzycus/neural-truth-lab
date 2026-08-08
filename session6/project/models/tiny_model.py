"""Tiny deterministic model — Embedding + MLP, no heavy deps."""

from __future__ import annotations

import math
from typing import Any


class TinyModel:
    """Minimal trainable model: embedding lookup + 2-layer MLP + softmax CE loss."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 16,
        hidden_dim: int = 32,
        seed: int = 42,
    ) -> None:
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.seed = seed
        self._step = 0
        self._lr = 0.01

        rng = self._make_rng(seed)
        self.embedding = [
            [self._gauss(rng) for _ in range(embed_dim)] for _ in range(vocab_size)
        ]
        self.w1 = [
            [self._gauss(rng) for _ in range(hidden_dim)] for _ in range(embed_dim)
        ]
        self.b1 = [0.0] * hidden_dim
        self.w2 = [
            [self._gauss(rng) for _ in range(vocab_size)] for _ in range(hidden_dim)
        ]
        self.b2 = [0.0] * vocab_size

    @staticmethod
    def _make_rng(seed: int) -> list[int]:
        return [seed]

    @staticmethod
    def _next(rng: list[int]) -> float:
        rng[0] = (rng[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return (rng[0] / 0x7FFFFFFF) * 2 - 1

    def _gauss(self, rng: list[int]) -> float:
        return self._next(rng) * 0.1

    def _embed(self, token_id: int) -> list[float]:
        return list(self.embedding[token_id % self.vocab_size])

    def _matvec(self, mat: list[list[float]], vec: list[float], bias: list[float]) -> list[float]:
        return [
            sum(mat[j][i] * vec[j] for j in range(len(vec))) + bias[i]
            for i in range(len(bias))
        ]

    def _relu(self, vec: list[float]) -> list[float]:
        return [max(0.0, v) for v in vec]

    def _softmax(self, logits: list[float]) -> list[float]:
        max_l = max(logits)
        exps = [math.exp(l - max_l) for l in logits]
        total = sum(exps)
        return [e / total for e in exps]

    def forward(self, token_ids: list[int]) -> tuple[list[float], float]:
        if len(token_ids) < 2:
            return [0.0] * self.vocab_size, 0.0

        total_loss = 0.0
        count = 0
        rng = self._make_rng(self.seed + self._step)

        for t in range(len(token_ids) - 1):
            inp = self._embed(token_ids[t])
            hidden = self._relu(self._matvec(self.w1, inp, self.b1))
            logits = self._matvec(self.w2, hidden, self.b2)
            target = token_ids[t + 1]
            probs = self._softmax(logits)
            prob = max(probs[target], 1e-10)
            total_loss -= math.log(prob)
            count += 1

        avg_loss = total_loss / count if count > 0 else 0.0
        last_inp = self._embed(token_ids[-2])
        hidden = self._relu(self._matvec(self.w1, last_inp, self.b1))
        logits = self._matvec(self.w2, hidden, self.b2)
        return logits, avg_loss

    def train_step(self, token_ids: list[int], attention_mask: list[int] | None = None) -> float:
        active = token_ids
        if attention_mask:
            active = [t for t, m in zip(token_ids, attention_mask) if m == 1]
        _, loss = self.forward(active)
        self._step += 1
        # ponytail: fake gradient step — nudge embedding by loss magnitude
        delta = self._lr * loss * 0.001
        for i in range(min(3, self.vocab_size)):
            for j in range(self.embed_dim):
                self.embedding[i][j] -= delta
        return loss

    def get_state(self) -> dict[str, Any]:
        return {
            "embedding": self.embedding,
            "w1": self.w1,
            "b1": self.b1,
            "w2": self.w2,
            "b2": self.b2,
            "step": self._step,
            "seed": self.seed,
        }

    def load_state(self, state: dict[str, Any]) -> None:
        self.embedding = state["embedding"]
        self.w1 = state["w1"]
        self.b1 = state["b1"]
        self.w2 = state["w2"]
        self.b2 = state["b2"]
        self._step = state["step"]

    def get_optimizer_state(self) -> dict[str, Any]:
        return {"step": self._step, "lr": self._lr}

    def load_optimizer_state(self, state: dict[str, Any]) -> None:
        self._step = state.get("step", self._step)
        self._lr = state.get("lr", self._lr)
