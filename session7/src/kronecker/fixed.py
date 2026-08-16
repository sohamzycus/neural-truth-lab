"""Fixed-window Kronecker baseline (Problem 3 reference implementation)."""

from __future__ import annotations

import math
from dataclasses import dataclass


CAPACITY = 32


def utf8_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def fixed_deterministic_features(text: str, capacity: int = CAPACITY) -> tuple[list[float], dict]:
    """Map string → fixed-size deterministic feature vector.

    Layout per slot i in [0, capacity):
      [byte/255, occupied_flag]
    Plus trailing overflow flag if len(bytes) > capacity.
    """
    raw = utf8_bytes(text)
    truncated = raw[:capacity]
    overflow = max(0, len(raw) - capacity)
    features: list[float] = []
    for i in range(capacity):
        if i < len(truncated):
            features.extend([truncated[i] / 255.0, 1.0])
        else:
            features.extend([0.0, 0.0])
    features.append(1.0 if overflow > 0 else 0.0)
    meta = {
        "byte_length": len(raw),
        "used_bytes": len(truncated),
        "capacity": capacity,
        "overflow_bytes": overflow,
        "truncated": overflow > 0,
        "waste_bytes": max(0, capacity - len(truncated)),
        "waste_ratio": max(0, capacity - len(truncated)) / capacity,
    }
    return features, meta


def project_deterministic(features: list[float], dim: int, seed: int = 42) -> list[float]:
    """Deterministic pseudo-random projection (fixed weights, not trainable)."""
    rng = _lcg(seed)
    weights = [[_gauss(rng) for _ in range(len(features))] for _ in range(dim)]
    return [
        sum(weights[i][j] * features[j] for j in range(len(features)))
        for i in range(dim)
    ]


def _lcg(seed: int) -> list[int]:
    return [seed & 0x7FFFFFFF]


def _gauss(rng: list[int]) -> float:
    rng[0] = (rng[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (rng[0] / 0x7FFFFFFF) * 2 - 1


@dataclass
class FixedKronecker:
    capacity: int = CAPACITY
    latent_dim: int = 64
    seed: int = 42

    def encode_deterministic(self, text: str) -> tuple[list[float], dict]:
        feats, meta = fixed_deterministic_features(text, self.capacity)
        latent = project_deterministic(feats, self.latent_dim, self.seed)
        meta["representation_size"] = len(feats)
        return latent, meta

    def collision_key(self, text: str) -> str:
        feats, _ = fixed_deterministic_features(text, self.capacity)
        return ",".join(f"{v:.6f}" for v in feats)
