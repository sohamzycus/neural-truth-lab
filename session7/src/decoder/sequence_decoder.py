"""Sequence-aware decoder (latent-conditioned recurrence over positions)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SequenceDecoder:
    latent_dim: int
    max_bytes: int = 256
    hidden: int = 96
    seed: int = 123
    lr: float = 0.06

    _w_xh: np.ndarray = field(init=False, repr=False)
    _w_hh: np.ndarray = field(init=False, repr=False)
    _b_h: np.ndarray = field(init=False, repr=False)
    _w_hy: np.ndarray = field(init=False, repr=False)
    _b_y: np.ndarray = field(init=False, repr=False)
    _w_init: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        h, d, x = self.hidden, self.latent_dim, self.latent_dim + 2
        scale = 0.08
        self._w_xh = rng.uniform(-scale, scale, (h, x))
        self._w_hh = rng.uniform(-scale, scale, (h, h))
        self._b_h = np.zeros(h)
        self._w_hy = rng.uniform(-scale, scale, (256, h))
        self._b_y = np.zeros(256)
        self._w_init = rng.uniform(-scale, scale, (h, d))

    @property
    def trainable_parameters(self) -> int:
        h, d, x = self.hidden, self.latent_dim, self.latent_dim + 2
        return h * x + h * h + h + 256 * h + 256 + h * d

    def _step(self, x: np.ndarray, h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        z = self._w_xh @ x + self._w_hh @ h + self._b_h
        h2 = np.maximum(0.0, z)
        logits = self._w_hy @ h2 + self._b_y
        return logits, h2

    def decode_bytes(self, latent: list[float], length: int | None = None) -> bytes:
        n = length or max(1, min(self.max_bytes, int(round(latent[0] * self.max_bytes)) if latent else 1))
        h = self._w_init @ np.array(latent, dtype=np.float64)
        out: list[int] = []
        for p in range(n):
            rel = p / max(n - 1, 1)
            x = np.array(list(latent) + [rel, 1.0], dtype=np.float64)
            logits, h = self._step(x, h)
            out.append(int(np.argmax(logits)))
        return bytes(out)

    def decode_string(self, latent: list[float], length: int | None = None) -> str:
        return self.decode_bytes(latent, length).decode("utf-8", errors="replace")

    def train_step(self, latent: list[float], target: bytes) -> float:
        n = len(target)
        h = self._w_init @ np.array(latent, dtype=np.float64)
        loss = 0.0
        d_w_xh = np.zeros_like(self._w_xh)
        d_w_hh = np.zeros_like(self._w_hh)
        d_b_h = np.zeros_like(self._b_h)
        d_w_hy = np.zeros_like(self._w_hy)
        d_b_y = np.zeros_like(self._b_y)
        d_w_init = np.zeros_like(self._w_init)
        dh_next = np.zeros(self.hidden)

        for p in range(n - 1, -1, -1):
            rel = p / max(n - 1, 1)
            x = np.array(list(latent) + [rel, 1.0], dtype=np.float64)
            # forward cache recomputed simply (ponytail: O(n) re-forward acceptable for POC)
            h = self._w_init @ np.array(latent, dtype=np.float64)
            hs: list[np.ndarray] = []
            xs: list[np.ndarray] = []
            for i in range(p + 1):
                rel_i = i / max(n - 1, 1)
                xi = np.array(list(latent) + [rel_i, 1.0], dtype=np.float64)
                logits_i, h = self._step(xi, h)
                xs.append(xi)
                hs.append(h)
            logits = logits_i
            tb = target[p]
            logits = logits - logits.max()
            exp_l = np.exp(logits)
            probs = exp_l / exp_l.sum()
            loss -= math.log(max(float(probs[tb]), 1e-12))
            grad_logits = probs
            grad_logits[tb] -= 1.0
            d_w_hy += np.outer(grad_logits, hs[-1])
            d_b_y += grad_logits
            grad_h = self._w_hy.T @ grad_logits + dh_next
            grad_z = grad_h * (hs[-1] > 0)
            d_w_xh += np.outer(grad_z, xs[-1])
            d_w_hh += np.outer(grad_z, hs[-2] if len(hs) > 1 else np.zeros(self.hidden))
            d_b_h += grad_z
            if p == 0:
                d_w_init += np.outer(grad_z, np.array(latent, dtype=np.float64))
            break  # ponytail: single-position gradient per step for speed

        scale = self.lr / max(n, 1)
        self._w_hy -= scale * d_w_hy
        self._b_y -= scale * d_b_y
        self._w_xh -= scale * d_w_xh
        self._w_hh -= scale * d_w_hh
        self._b_h -= scale * d_b_h
        self._w_init -= scale * d_w_init
        return loss / max(n, 1)

    def train(self, pairs: list[tuple[list[float], bytes]], steps: int = 300, full_epoch: bool = False) -> list[float]:
        losses: list[float] = []
        rng = random.Random(self.seed)
        if full_epoch:
            shuffled = list(pairs)
            for _ in range(steps):
                rng.shuffle(shuffled)
                step_loss = sum(self.train_step(lat, tgt) for lat, tgt in shuffled)
                losses.append(step_loss / max(len(shuffled), 1))
            return losses
        for _ in range(steps):
            lat, tgt = pairs[rng.randint(0, len(pairs) - 1)]
            losses.append(self.train_step(lat, tgt))
        return losses
