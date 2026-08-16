"""Lightweight autoregressive byte decoder."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import numpy as np


@dataclass
class AutoregressiveDecoder:
    latent_dim: int
    max_bytes: int = 256
    hidden: int = 96
    seed: int = 123
    lr: float = 0.06

    _w_emb: np.ndarray = field(init=False, repr=False)
    _w_xh: np.ndarray = field(init=False, repr=False)
    _w_hh: np.ndarray = field(init=False, repr=False)
    _b_h: np.ndarray = field(init=False, repr=False)
    _w_hy: np.ndarray = field(init=False, repr=False)
    _b_y: np.ndarray = field(init=False, repr=False)
    _w_z: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        h, d = self.hidden, self.latent_dim
        s = 0.08
        self._w_emb = rng.uniform(-s, s, (h, 256))
        self._w_xh = rng.uniform(-s, s, (h, h + d))
        self._w_hh = rng.uniform(-s, s, (h, h))
        self._b_h = np.zeros(h)
        self._w_hy = rng.uniform(-s, s, (256, h))
        self._b_y = np.zeros(256)
        self._w_z = rng.uniform(-s, s, (h, d))

    @property
    def trainable_parameters(self) -> int:
        h, d = self.hidden, self.latent_dim
        return h * 256 + h * (h + d) + h * h + h + 256 * h + 256 + h * d

    def _forward(self, latent: np.ndarray, prev_byte: int, h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        emb = self._w_emb[:, prev_byte]
        inp = np.concatenate([emb, latent])
        z = self._w_xh @ inp + self._w_hh @ h + self._b_h
        h2 = np.maximum(0.0, z)
        logits = self._w_hy @ h2 + self._b_y
        return logits, h2

    def decode_bytes(self, latent: list[float], length: int | None = None) -> bytes:
        n = length or 1
        z = np.array(latent, dtype=np.float64)
        h = self._w_z @ z
        prev = 0
        out: list[int] = []
        for _ in range(n):
            logits, h = self._forward(z, prev, h)
            prev = int(np.argmax(logits))
            out.append(prev)
        return bytes(out)

    def decode_string(self, latent: list[float], length: int | None = None) -> str:
        return self.decode_bytes(latent, length).decode("utf-8", errors="replace")

    def train_step(self, latent: list[float], target: bytes) -> float:
        z = np.array(latent, dtype=np.float64)
        h = self._w_z @ z
        prev = 0
        loss = 0.0
        d_w_emb = np.zeros_like(self._w_emb)
        d_w_xh = np.zeros_like(self._w_xh)
        d_w_hh = np.zeros_like(self._w_hh)
        d_b_h = np.zeros_like(self._b_h)
        d_w_hy = np.zeros_like(self._w_hy)
        d_b_y = np.zeros_like(self._b_y)
        d_w_z = np.zeros_like(self._w_z)

        for tb in target:
            logits, h_new = self._forward(z, prev, h)
            logits = logits - logits.max()
            exp_l = np.exp(logits)
            probs = exp_l / exp_l.sum()
            loss -= math.log(max(float(probs[tb]), 1e-12))
            grad_logits = probs
            grad_logits[tb] -= 1.0
            d_w_hy += np.outer(grad_logits, h_new)
            d_b_y += grad_logits
            grad_h = self._w_hy.T @ grad_logits
            grad_z = grad_h * (h_new > 0)
            emb = self._w_emb[:, prev]
            inp = np.concatenate([emb, z])
            d_w_xh += np.outer(grad_z, inp)
            d_w_hh += np.outer(grad_z, h)
            d_b_h += grad_z
            d_w_emb[:, prev] += (self._w_xh.T @ grad_z)[: self.hidden]
            d_w_z += (self._w_xh.T @ grad_z)[self.hidden :]
            h = h_new
            prev = tb

        scale = self.lr / max(len(target), 1)
        self._w_hy -= scale * d_w_hy
        self._b_y -= scale * d_b_y
        self._w_xh -= scale * d_w_xh
        self._w_hh -= scale * d_w_hh
        self._b_h -= scale * d_b_h
        self._w_emb -= scale * d_w_emb
        self._w_z -= scale * d_w_z
        return loss / max(len(target), 1)

    def train(self, pairs: list[tuple[list[float], bytes]], steps: int = 300, full_epoch: bool = False) -> list[float]:
        losses: list[float] = []
        rng = random.Random(self.seed)
        if full_epoch:
            shuffled = list(pairs)
            for _ in range(steps):
                rng.shuffle(shuffled)
                losses.append(sum(self.train_step(l, t) for l, t in shuffled) / max(len(shuffled), 1))
            return losses
        for _ in range(steps):
            l, t = pairs[rng.randint(0, len(pairs) - 1)]
            losses.append(self.train_step(l, t))
        return losses
