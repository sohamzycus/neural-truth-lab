"""Position-wise byte decoder for reversible embedding experiments (Problem 5)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

try:
    import numpy as np

    _HAS_NUMPY = True
except ImportError:  # pragma: no cover
    _HAS_NUMPY = False


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)


@dataclass
class ByteDecoder:
    latent_dim: int
    max_bytes: int = 256
    seed: int = 123
    lr: float = 0.08
    hidden: int = 96
    _w1: list[list[float]] = field(init=False, repr=False)
    _b1: list[float] = field(init=False, repr=False)
    _w2: list[list[float]] = field(init=False, repr=False)
    _b2: list[float] = field(init=False, repr=False)
    _w_len: list[float] = field(init=False, repr=False)
    _b_len: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        rng = random.Random(self.seed)
        in_dim = self.latent_dim + 2
        self._w1 = [[rng.uniform(-0.08, 0.08) for _ in range(in_dim)] for _ in range(self.hidden)]
        self._b1 = [0.0] * self.hidden
        self._w2 = [[rng.uniform(-0.08, 0.08) for _ in range(self.hidden)] for _ in range(256)]
        self._b2 = [0.0] * 256
        self._w_len = [rng.uniform(-0.08, 0.08) for _ in range(self.latent_dim)]
        self._b_len = 0.0

    @property
    def trainable_parameters(self) -> int:
        in_dim = self.latent_dim + 2
        return in_dim * self.hidden + self.hidden + self.hidden * 256 + 256 + self.latent_dim + 1

    def _input_vec(self, latent: list[float], pos: int, max_len: int) -> list[float]:
        rel = pos / max(max_len - 1, 1)
        occ = 1.0 if pos < max_len else 0.0
        return list(latent) + [rel, occ]

    def _forward_pos(self, latent: list[float], pos: int, max_len: int) -> tuple[list[float], list[float]]:
        x = self._input_vec(latent, pos, max_len)
        hidden = []
        for i in range(self.hidden):
            s = self._b1[i] + sum(self._w1[i][j] * x[j] for j in range(len(x)))
            hidden.append(max(0.0, s))
        logits = [
            self._b2[c] + sum(self._w2[c][j] * hidden[j] for j in range(self.hidden))
            for c in range(256)
        ]
        return logits, hidden

    def predict_length(self, latent: list[float]) -> int:
        z = self._b_len + sum(w * latent[i] for i, w in enumerate(self._w_len))
        length = int(round(_sigmoid(z) * self.max_bytes))
        return max(1, min(self.max_bytes, length))

    def decode_bytes(self, latent: list[float], length: int | None = None) -> bytes:
        n = length if length is not None else self.predict_length(latent)
        out: list[int] = []
        for p in range(n):
            logits, _ = self._forward_pos(latent, p, n)
            out.append(max(range(256), key=lambda c: logits[c]))
        return bytes(out)

    def decode_string(self, latent: list[float], length: int | None = None) -> str:
        return self.decode_bytes(latent, length).decode("utf-8", errors="replace")

    def _train_step_numpy(self, latent: list[float], target: bytes) -> float:
        assert _HAS_NUMPY
        n = len(target)
        in_dim = self.latent_dim + 2
        W1 = np.array(self._w1, dtype=np.float64)
        b1 = np.array(self._b1, dtype=np.float64)
        W2 = np.array(self._w2, dtype=np.float64)
        b2 = np.array(self._b2, dtype=np.float64)
        loss = 0.0
        dW1 = np.zeros_like(W1)
        db1 = np.zeros_like(b1)
        dW2 = np.zeros_like(W2)
        db2 = np.zeros_like(b2)

        for p, tb in enumerate(target):
            x = np.array(self._input_vec(latent, p, n), dtype=np.float64)
            z1 = W1 @ x + b1
            h = np.maximum(0.0, z1)
            logits = W2 @ h + b2
            logits -= logits.max()
            exp_l = np.exp(logits)
            probs = exp_l / exp_l.sum()
            loss -= math.log(max(float(probs[tb]), 1e-12))
            grad_logits = probs
            grad_logits[tb] -= 1.0
            dW2 += np.outer(grad_logits, h)
            db2 += grad_logits
            grad_h = W2.T @ grad_logits
            grad_z1 = grad_h * (z1 > 0).astype(np.float64)
            dW1 += np.outer(grad_z1, x)
            db1 += grad_z1

        scale = self.lr / max(n, 1)
        W2 -= scale * dW2
        b2 -= scale * db2
        W1 -= scale * dW1
        b1 -= scale * db1
        self._w1 = W1.tolist()
        self._b1 = b1.tolist()
        self._w2 = W2.tolist()
        self._b2 = b2.tolist()
        return float(loss / max(n, 1))

    def train_step(self, latent: list[float], target: bytes) -> float:
        if _HAS_NUMPY:
            return self._train_step_numpy(latent, target)
        n = len(target)
        loss = 0.0
        for p, tb in enumerate(target):
            logits, _ = self._forward_pos(latent, p, n)
            max_l = max(logits)
            exps = [math.exp(l - max_l) for l in logits]
            total = sum(exps)
            probs = [e / total for e in exps]
            loss -= math.log(max(probs[tb], 1e-12))
            for c in range(256):
                grad = probs[c] - (1.0 if c == tb else 0.0)
                self._b2[c] -= self.lr * grad * 0.05
        return loss / max(n, 1)

    def train(self, pairs: list[tuple[list[float], bytes]], steps: int = 300, full_epoch: bool = False) -> list[float]:
        losses: list[float] = []
        rng = random.Random(self.seed)
        if full_epoch:
            shuffled = list(pairs)
            for step in range(steps):
                rng.shuffle(shuffled)
                step_loss = 0.0
                for latent, target in shuffled:
                    step_loss += self.train_step(latent, target)
                losses.append(step_loss / max(len(shuffled), 1))
                if step > 0 and step % 50 == 0:
                    self.lr *= 0.98
            return losses
        for step in range(steps):
            latent, target = pairs[rng.randint(0, len(pairs) - 1)]
            losses.append(self.train_step(latent, target))
            if step > 0 and step % 200 == 0:
                self.lr *= 0.95
        return losses
