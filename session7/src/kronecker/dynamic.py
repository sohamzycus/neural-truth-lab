"""Dynamic Kronecker — variable-length byte encoding with fixed latent (Option A)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from kronecker.fixed import project_deterministic, _lcg, _gauss


def dynamic_deterministic_features(
    text: str,
    max_bytes: int = 256,
) -> tuple[list[float], dict]:
    """Position-aware byte features without truncation (up to max_bytes).

    Per byte i: [byte/255, rel_position, occupied=1]
    Header: [length_norm, char_count_norm]
    """
    raw = text.encode("utf-8")
    char_count = len(text)
    byte_len = len(raw)
    overflow = max(0, byte_len - max_bytes)
    used = raw[:max_bytes]

    features = [byte_len / max_bytes, char_count / max(max_bytes, 1)]
    for i, b in enumerate(used):
        rel_pos = i / max(len(used) - 1, 1)
        features.extend([b / 255.0, rel_pos, 1.0])
    # pad remaining slots
    slots = max_bytes
    for i in range(len(used), slots):
        features.extend([0.0, i / max(slots - 1, 1), 0.0])
    features.append(1.0 if overflow > 0 else 0.0)

    meta = {
        "byte_length": byte_len,
        "char_length": char_count,
        "used_bytes": len(used),
        "max_bytes": max_bytes,
        "overflow_bytes": overflow,
        "truncated": overflow > 0,
        "waste_bytes": 0,  # dynamic: no fixed-slot waste
        "waste_ratio": 0.0,
        "representation_size": len(features),
    }
    return features, meta


@dataclass
class DynamicKronecker:
    max_bytes: int = 256
    latent_dim: int = 64
    seed: int = 42
    project_latent: bool = True

    def encode_deterministic(self, text: str) -> tuple[list[float], dict]:
        feats, meta = dynamic_deterministic_features(text, self.max_bytes)
        if self.project_latent:
            latent = project_deterministic(feats, self.latent_dim, self.seed + 1)
        else:
            latent = feats
            meta["latent_dim"] = len(feats)
        return latent, meta

    def collision_key(self, text: str) -> str:
        feats, _ = dynamic_deterministic_features(text, self.max_bytes)
        return ",".join(f"{v:.6f}" for v in feats)


def length_aware_pool(byte_values: list[int], dim: int, seed: int = 7) -> list[float]:
    """Weighted sum-pool of byte+position embeddings → fixed dim (pre-projection)."""
    if not byte_values:
        return [0.0] * dim
    rng = _lcg(seed)
    # ponytail: fixed random position vectors per slot index mod dim
    acc = [0.0] * dim
    n = len(byte_values)
    for i, b in enumerate(byte_values):
        for d in range(dim):
            w = math.sin((i + 1) * (d + 1) * 0.17) + math.cos(b * (d + 1) * 0.031)
            acc[d] += (b / 255.0) * w
    norm = math.sqrt(sum(x * x for x in acc)) or 1.0
    return [x / norm for x in acc]
