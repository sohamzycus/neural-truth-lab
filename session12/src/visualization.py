"""Plots from simulator output only."""

from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt

from .experiments import ExperimentRecord


def _filter(records: List[ExperimentRecord], prefix: str) -> List[ExperimentRecord]:
    return [r for r in records if r.experiment_id.startswith(prefix) or r.strategy == prefix]


def plot_peak_memory(records: List[ExperimentRecord], out: Path) -> None:
    core = [r for r in records if r.experiment_id in ("exp1_baseline_dp", "exp2_zero1", "exp3_zero2", "exp4_zero3")]
    labels = [r.strategy.replace("_", " ") for r in core]
    peaks = [r.peak_memory_per_gpu / 1e6 for r in core]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, peaks, color=["#4c72b0", "#55a868", "#c44e52", "#8172b2"])
    ax.set_ylabel("Peak memory per GPU (MB)")
    ax.set_title("Peak memory per GPU (simulation)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_memory_breakdown(records: List[ExperimentRecord], out: Path) -> None:
    from .config import SimConfig
    from .simulation import run_strategy

    strategies = ["baseline_dp", "zero1", "zero2", "zero3"]
    cfg = SimConfig()
    components = ["parameters", "gradients", "optimizer", "activations", "buffers"]
    data = {c: [] for c in components}
    for s in strategies:
        m = run_strategy(s, cfg)
        b = m.memory_breakdown
        for c in components:
            data[c].append(b.get(c, 0) / 1e6)
    x = range(len(strategies))
    fig, ax = plt.subplots(figsize=(9, 4))
    bottom = [0.0] * len(strategies)
    colors = ["#4c72b0", "#55a868", "#c44e52", "#ccb974", "#64b5cd"]
    for i, comp in enumerate(components):
        ax.bar(x, data[comp], bottom=bottom, label=comp, color=colors[i % len(colors)])
        bottom = [b + v for b, v in zip(bottom, data[comp])]
    ax.set_xticks(list(x))
    ax.set_xticklabels(strategies)
    ax.set_ylabel("Memory (MB)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title("Per-GPU memory breakdown (rank 0, simulation)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_comm_volume(records: List[ExperimentRecord], out: Path) -> None:
    core = [r for r in records if r.experiment_id in ("exp1_baseline_dp", "exp2_zero1", "exp3_zero2", "exp4_zero3")]
    labels = [r.strategy for r in core]
    vols = [r.communication_bytes / 1e6 for r in core]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, vols, color="#dd8452")
    ax.set_ylabel("Communication volume (MB per step)")
    ax.set_title("Communication volume (simulation assumption)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_compute_vs_comm(records: List[ExperimentRecord], out: Path) -> None:
    core = [r for r in records if r.experiment_id in ("exp1_baseline_dp", "exp2_zero1", "exp3_zero2", "exp4_zero3")]
    labels = [r.strategy for r in core]
    comp = [r.compute_time for r in core]
    comm = [r.communication_time for r in core]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, comp, label="simulated compute time")
    ax.bar(labels, comm, bottom=comp, label="simulated comm time")
    ax.set_ylabel("Seconds (simulation)")
    ax.legend()
    ax.set_title("Compute vs communication time")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_comm_fraction_sweep(records: List[ExperimentRecord], out: Path) -> None:
    sweep = [r for r in records if r.experiment_id.startswith("exp8_")]
    if not sweep:
        return
    xs = [r.model_parameters / 1e6 for r in sweep]
    ys = [r.communication_fraction for r in sweep]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, marker="o")
    ax.set_xlabel("Model parameters (millions)")
    ax.set_ylabel("Communication fraction")
    ax.set_title("ZeRO-3 communication fraction vs model size")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_bucket_effect(records: List[ExperimentRecord], out: Path) -> None:
    buckets = [r for r in records if "bucket" in r.experiment_id]
    if len(buckets) < 2:
        return
    labels = [r.notes for r in buckets]
    times = [r.total_step_time for r in buckets]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(len(labels)), times, tick_label=labels)
    ax.set_ylabel("Total step time (simulation)")
    ax.set_title("Conceptual overlap: bucket size effect on ZeRO-3")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_scaling(records: List[ExperimentRecord], out: Path) -> None:
    from .experiments import scaling_sweep

    sweep = scaling_sweep()
    ws = [r.world_size for r in sweep]
    times = [r.total_step_time for r in sweep]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(ws, times, marker="s")
    ax.set_xlabel("Virtual GPUs (world size)")
    ax.set_ylabel("Baseline DP step time (simulation)")
    ax.set_title("Scaling 1→32 GPUs (baseline)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_overlap_timeline(out: Path, bucket_size: int = 500_000, total_bytes: int = 4_000_000) -> None:
    """Conceptual overlap simulation — not DeepSpeed's scheduler."""
    import numpy as np

    num_buckets = max(1, (total_bytes + bucket_size - 1) // bucket_size)
    fig, ax = plt.subplots(figsize=(9, 2.5))
    t = 0.0
    for i in range(num_buckets):
        ax.broken_barh([(t, 0.4)], (1, 0.3), facecolors="#55a868", label="COMPUTE" if i == 0 else None)
        ax.broken_barh([(t + 0.2, 0.5)], (0, 0.3), facecolors="#c44e52", label="COMM" if i == 0 else None)
        t += 1.0
    ax.set_xlabel("Conceptual time")
    ax.set_yticks([0.3, 1.15])
    ax.set_yticklabels(["communication", "compute"])
    ax.set_title("Conceptual overlap simulation (bucketed backward)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def generate_all_plots(records: List[ExperimentRecord], figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_peak_memory(records, figures_dir / "peak_memory_per_gpu.png")
    plot_memory_breakdown(records, figures_dir / "memory_breakdown.png")
    plot_comm_volume(records, figures_dir / "communication_volume.png")
    plot_compute_vs_comm(records, figures_dir / "compute_vs_comm.png")
    plot_comm_fraction_sweep(records, figures_dir / "comm_fraction_model_sweep.png")
    plot_bucket_effect(records, figures_dir / "bucket_size_effect.png")
    plot_scaling(records, figures_dir / "scaling_baseline.png")
    plot_overlap_timeline(figures_dir / "overlap_timeline.png")
