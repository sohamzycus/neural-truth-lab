"""Loss and routing figures for Session 14."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_loss_curve(
    dense_csv: Path,
    moe_csv: Path,
    dense_steps: int,
    out_path: Path,
    eval_points: dict[str, float],
) -> None:
    d = pd.read_csv(dense_csv)
    m = pd.read_csv(moe_csv)
    fig, ax = plt.subplots(figsize=(9.5, 5))

    ax.plot(d["step"], d["loss"], color="#2563eb", lw=1.8, label="Dense training (batch loss)")
    ax.plot(m["step"], m["loss"], color="#dc2626", lw=1.8, label="MoE continued training (batch loss)")

    conv_x = dense_steps - 0.5
    ax.axvline(conv_x, color="#6b7280", ls="--", lw=1.2)
    ymax = max(
        d["loss"].max(),
        m["loss"].max(),
        max(eval_points.values()),
    ) * 1.05
    ax.set_ylim(0, ymax)
    ax.text(0, ymax * 0.98, "DENSE TRAINING", fontsize=8, color="#2563eb", va="top")
    ax.text(conv_x + 2, ymax * 0.98, "MOE CONTINUED TRAINING", fontsize=8, color="#dc2626", va="top")
    ax.text(conv_x - 25, ymax * 0.88, "DENSE → MoE\nCONVERSION", fontsize=7, color="#6b7280", ha="center")

    markers = {
        "dense_initial": ("o", "#1d4ed8"),
        "dense_final": ("s", "#1d4ed8"),
        "moe_at_conversion": ("^", "#059669"),
        "moe_final": ("D", "#b91c1c"),
    }
    x_map = {
        "dense_initial": 0,
        "dense_final": dense_steps - 1,
        "moe_at_conversion": dense_steps - 1,
        "moe_final": int(m["step"].max()),
    }
    for key, (marker, color) in markers.items():
        if key not in eval_points:
            continue
        ax.scatter(
            [x_map[key]],
            [eval_points[key]],
            marker=marker,
            s=70,
            color=color,
            edgecolors="white",
            linewidths=0.6,
            zorder=6,
            label=f"Held-out eval: {key.replace('_', ' ')}",
        )
        ax.annotate(
            f"{eval_points[key]:.3f}",
            (x_map[key], eval_points[key]),
            textcoords="offset points",
            xytext=(4, 6),
            fontsize=7,
        )

    ax.set_xlabel("Global training step")
    ax.set_ylabel("Loss")
    ax.set_title("Dense train → conversion (held-out eval) → MoE continued train")
    ax.legend(loc="upper right", fontsize=7, ncol=1)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_expert_utilization(routing_csv: Path, out_path: Path) -> None:
    df = pd.read_csv(routing_csv)
    if df.empty:
        return
    last = df.iloc[-1]
    util = json.loads(last["expert_utilization"])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(len(util)), util, color="#7c3aed")
    ax.set_xlabel("Expert index")
    ax.set_ylabel("Fraction of token routes")
    ax.set_title(f"Expert utilization (final MoE step, top_k={int(last['top_k'])})")
    ax.set_xticks(range(len(util)))
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
