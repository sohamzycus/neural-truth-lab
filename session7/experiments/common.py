"""Shared experiment utilities for Session 7."""

from __future__ import annotations

import math
import random
import time
from typing import Any, Protocol

from decoder.byte_decoder import ByteDecoder
from metrics.reconstruction import reconstruction_report


class DecoderProtocol(Protocol):
    def train(self, pairs: list[tuple[list[float], bytes]], steps: int = 300, full_epoch: bool = False) -> list[float]: ...
    def decode_string(self, latent: list[float], length: int | None = None) -> str: ...
    @property
    def trainable_parameters(self) -> int: ...


DEFAULT_SEED = 42
DEFAULT_STEPS = 2000
FULL_FEATURE_EPOCHS = 80


def make_decoder(kind: str, latent_dim: int, seed: int = 123) -> DecoderProtocol:
    if kind == "position_mlp":
        return ByteDecoder(latent_dim=latent_dim, seed=seed)
    if kind == "sequence":
        from decoder.sequence_decoder import SequenceDecoder
        return SequenceDecoder(latent_dim=latent_dim, seed=seed)
    if kind == "autoregressive":
        from decoder.autoregressive_decoder import AutoregressiveDecoder
        return AutoregressiveDecoder(latent_dim=latent_dim, seed=seed)
    raise ValueError(f"unknown decoder: {kind}")


def aggregate_reports(reports: list[dict]) -> dict:
    n = max(len(reports), 1)
    exact = sum(1 for r in reports if r["string_exact_match"])
    return {
        "count": len(reports),
        "string_exact_match_rate": round(exact / n, 4),
        "avg_byte_accuracy": round(sum(r["byte_accuracy"] for r in reports) / n, 4),
        "avg_char_accuracy": round(sum(r["char_accuracy"] for r in reports) / n, 4),
        "avg_edit_distance": round(sum(r["edit_distance"] for r in reports) / n, 4),
        "length_preserved_rate": round(sum(1 for r in reports if r["length_preserved"]) / n, 4),
    }


def eval_strings(encoder, decoder: DecoderProtocol, strings: list[str], known_length: bool = True) -> dict:
    reports = []
    for s in strings:
        latent, meta = encoder.encode_deterministic(s)
        blen = len(s.encode("utf-8"))
        decoded = decoder.decode_string(latent, length=blen if known_length else None)
        rep = reconstruction_report(s, decoded)
        rep["truncated_input"] = meta.get("truncated", False)
        rep["byte_length"] = blen
        reports.append(rep)
    out = aggregate_reports(reports)
    out["samples"] = reports[:3]
    return out


def train_and_eval(
    encoder,
    train: list[str],
    val: list[str],
    test: list[str],
    *,
    decoder_kind: str = "position_mlp",
    steps: int = DEFAULT_STEPS,
    seed: int = DEFAULT_SEED,
    full_epoch: bool = False,
    known_length_eval: bool = True,
) -> dict:
    pairs = [(encoder.encode_deterministic(s)[0], s.encode("utf-8")) for s in train]
    latent_dim = len(pairs[0][0]) if pairs else getattr(encoder, "latent_dim", 64)
    decoder = make_decoder(decoder_kind, latent_dim, seed=seed + 1)
    t0 = time.perf_counter()
    losses = decoder.train(pairs, steps=steps, full_epoch=full_epoch)
    train_time = time.perf_counter() - t0
    val_loss = _eval_loss(decoder, val, encoder)
    return {
        "decoder_kind": decoder_kind,
        "latent_dim": latent_dim,
        "trainable_parameters_decoder": decoder.trainable_parameters,
        "train_time_sec": round(train_time, 3),
        "final_train_loss": round(losses[-1], 6) if losses else None,
        "validation_loss": round(val_loss, 6) if val_loss is not None else None,
        "train_eval": eval_strings(encoder, decoder, train, known_length_eval),
        "val_eval": eval_strings(encoder, decoder, val, known_length_eval),
        "test_eval": eval_strings(encoder, decoder, test, known_length_eval),
    }


def _eval_loss(decoder: DecoderProtocol, strings: list[str], encoder) -> float | None:
    if not strings or not hasattr(decoder, "train_step"):
        return None
    total = 0.0
    for s in strings:
        latent, _ = encoder.encode_deterministic(s)
        total += decoder.train_step(latent, s.encode("utf-8"))  # type: ignore[attr-defined]
    return total / len(strings)


def length_bucket(byte_len: int) -> str:
    bounds = [(1, 4), (5, 8), (9, 16), (17, 32), (33, 64), (65, 128), (129, 256)]
    for lo, hi in bounds:
        if lo <= byte_len <= hi:
            return f"{lo}-{hi}"
    return "257+"


def bucket_by_length(strings: list[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for s in strings:
        blen = len(s.encode("utf-8"))
        buckets.setdefault(length_bucket(blen), []).append(s)
    return buckets
