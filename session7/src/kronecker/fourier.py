"""Fourier byte-signal baseline (Problem 4 supporting experiment)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from kronecker.fixed import project_deterministic


def _dft_magnitude(signal: list[float]) -> list[float]:
    n = len(signal)
    mags: list[float] = []
    for k in range(n // 2 + 1):
        re = sum(signal[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
        im = sum(signal[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
        mags.append(math.sqrt(re * re + im * im) / n)
    return mags


def _dft_complex(signal: list[float]) -> list[tuple[float, float]]:
    n = len(signal)
    out: list[tuple[float, float]] = []
    for k in range(n // 2 + 1):
        re = sum(signal[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
        im = sum(signal[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
        out.append((re / n, im / n))
    return out


def fourier_deterministic_features(
    text: str, signal_len: int = 64, include_phase: bool = False
) -> tuple[list[float], dict]:
    raw = text.encode("utf-8")
    sig = [raw[i] / 255.0 if i < len(raw) else 0.0 for i in range(signal_len)]
    if include_phase:
        features: list[float] = []
        for re, im in _dft_complex(sig):
            mag = math.sqrt(re * re + im * im)
            phase = math.atan2(im, re) if mag > 1e-9 else 0.0
            features.extend([mag, phase / math.pi])
    else:
        features = _dft_magnitude(sig)
    meta = {
        "byte_length": len(raw),
        "signal_len": signal_len,
        "truncated": len(raw) > signal_len,
        "overflow_bytes": max(0, len(raw) - signal_len),
        "include_phase": include_phase,
    }
    return features, meta


def fourier_deterministic_features_legacy(text: str, signal_len: int = 64) -> tuple[list[float], dict]:
    return fourier_deterministic_features(text, signal_len, include_phase=False)


@dataclass
class FourierKronecker:
    signal_len: int = 64
    latent_dim: int = 64
    seed: int = 99
    include_phase: bool = False

    def encode_deterministic(self, text: str) -> tuple[list[float], dict]:
        feats, meta = fourier_deterministic_features(text, self.signal_len, self.include_phase)
        latent = project_deterministic(feats, self.latent_dim, self.seed)
        meta["representation_size"] = len(feats)
        return latent, meta

    def collision_key(self, text: str) -> str:
        feats, _ = fourier_deterministic_features(text, self.signal_len, self.include_phase)
        return ",".join(f"{v:.6f}" for v in feats)
