"""Deterministic inverse of dynamic feature vectors (upper bound for Problem 5)."""

from __future__ import annotations

from kronecker.dynamic import dynamic_deterministic_features


def inverse_dynamic_features(features: list[float], max_bytes: int = 256) -> bytes:
    """Recover UTF-8 bytes from a dynamic Kronecker feature vector."""
    byte_len = int(round(features[0] * max_bytes))
    out: list[int] = []
    offset = 2
    for _ in range(max_bytes):
        b_norm = features[offset]
        occupied = features[offset + 2]
        offset += 3
        if occupied > 0.5:
            out.append(int(round(b_norm * 255)))
    return bytes(out[:byte_len])


def deterministic_roundtrip(text: str, max_bytes: int = 256) -> tuple[str, bool]:
    feats, _ = dynamic_deterministic_features(text, max_bytes)
    recovered = inverse_dynamic_features(feats, max_bytes).decode("utf-8", errors="replace")
    return recovered, recovered == text
