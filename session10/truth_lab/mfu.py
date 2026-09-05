"""MFU estimation for the tiny model."""

from __future__ import annotations

import platform
import time
from dataclasses import dataclass
from typing import List

import torch

from truth_lab.config import LabConfig
from truth_lab.data import TinyCorpus, make_batch
from truth_lab.model import TinyGPT


@dataclass
class MFUReport:
    measured_seconds: float
    steps: int
    batch_size: int
    block_size: int
    params: int
    estimated_flops_per_step: float
    achieved_flops_per_sec: float
    hardware_peak_flops_per_sec: float
    mfu: float
    device: str
    notes: List[str]


def estimate_transformer_flops(cfg: LabConfig, vocab_size: int, batch_size: int) -> float:
    """
    Rough FLOPs per training step (forward + backward ≈ 3× forward).

    Forward per token (Kaplan et al. style approximation):
      - attention: 4 * B * T * D^2 + 2 * B * T^2 * D
      - MLP (4x expansion): 8 * B * T * D^2
      - embeddings + lm_head: 2 * B * T * D * V
    """
    b, t, d, l, v = batch_size, cfg.block_size, cfg.n_embd, cfg.n_layer, vocab_size
    attn = 4 * b * t * d * d + 2 * b * t * t * d
    mlp = 8 * b * t * d * d
    head = 2 * b * t * d * v
    forward = l * (attn + mlp) + head
    return 3 * forward


def hardware_peak_flops(device: str) -> tuple[float, str]:
    """Best-effort peak FLOP/s for MFU denominator."""
    if device == "cuda" and torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        props = torch.cuda.get_device_properties(0)
        peak = 2.0 * props.multi_processor_count * 128 * props.clock_rate * 1e3
        return peak, f"CUDA {name} (estimated FP32 peak)"
    if device == "mps":
        return 3.5e12, f"MPS / Apple Silicon (estimated FP32 peak, {platform.machine()})"
    return 1.0e11, "CPU (conservative estimate)"


def verify_mfu_report(report: MFUReport, rtol: float = 1e-6) -> dict:
    """Sanity-check MFU arithmetic."""
    total_flops = report.estimated_flops_per_step * report.steps
    achieved = total_flops / report.measured_seconds
    mfu = achieved / report.hardware_peak_flops_per_sec
    achieved_ok = abs(achieved - report.achieved_flops_per_sec) / max(report.achieved_flops_per_sec, 1e-12) < rtol
    mfu_ok = abs(mfu - report.mfu) < rtol
    in_range = 0.0 <= report.mfu <= 1.0
    return {
        "achieved_matches_formula": achieved_ok,
        "mfu_matches_formula": mfu_ok,
        "mfu_in_valid_range": in_range,
        "recomputed_achieved": achieved,
        "recomputed_mfu": mfu,
        "pass": achieved_ok and mfu_ok and in_range,
    }


def measure_mfu(
    model: TinyGPT,
    corpus: TinyCorpus,
    cfg: LabConfig,
    steps: int = 50,
    batch_size: int = 2,
    warmup: int = 5,
) -> MFUReport:
    device = torch.device(cfg.device)
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate)
    flops_per_step = estimate_transformer_flops(cfg, corpus.vocab_size, batch_size)
    peak, peak_note = hardware_peak_flops(cfg.device)

    notes = [
        "MFU is an estimate based on the assumptions documented here.",
        "FLOP count uses analytical transformer approximation (3× forward for train step).",
        "Formula: achieved_FLOPs/s = (FLOPs_per_step × steps) / measured_seconds",
        "Formula: MFU = achieved_FLOPs/s / hardware_peak_FLOPs/s",
        peak_note,
        "40% is not a realistic target for this tiny educational workload.",
    ]

    for i in range(warmup):
        x, y, m = make_batch(corpus, batch_size, cfg.block_size, cfg.seed + 9000 + i)
        x, y, m = x.to(device), y.to(device), m.to(device)
        optimizer.zero_grad(set_to_none=True)
        _, trace = model(x, targets=y, mask=m, trace=True)
        assert trace is not None and trace.loss is not None
        trace.loss.backward()
        optimizer.step()
        if cfg.device == "cuda":
            torch.cuda.synchronize()
        elif cfg.device == "mps":
            torch.mps.synchronize()

    t0 = time.perf_counter()
    for i in range(steps):
        x, y, m = make_batch(corpus, batch_size, cfg.block_size, cfg.seed + 10000 + i)
        x, y, m = x.to(device), y.to(device), m.to(device)
        optimizer.zero_grad(set_to_none=True)
        _, trace = model(x, targets=y, mask=m, trace=True)
        assert trace is not None and trace.loss is not None
        trace.loss.backward()
        optimizer.step()
    if cfg.device == "cuda":
        torch.cuda.synchronize()
    elif cfg.device == "mps":
        torch.mps.synchronize()
    elapsed = time.perf_counter() - t0

    achieved = (flops_per_step * steps) / elapsed
    mfu = achieved / peak if peak > 0 else 0.0

    return MFUReport(
        measured_seconds=elapsed,
        steps=steps,
        batch_size=batch_size,
        block_size=cfg.block_size,
        params=model.count_parameters(),
        estimated_flops_per_step=flops_per_step,
        achieved_flops_per_sec=achieved,
        hardware_peak_flops_per_sec=peak,
        mfu=mfu,
        device=cfg.device,
        notes=notes,
    )
