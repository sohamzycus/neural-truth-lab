"""EXP-LR-001 — Width / learning-rate landscape."""

from __future__ import annotations

import math
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.core.data import TinyCorpus
from src.core.mode_config import lr_grid_points, lr_train_steps, lr_widths
from src.core.schemas import DataConfig, LabConfig, ModelConfig, OptimizerConfig, RuntimeConfig, ScheduleConfig
from src.core.training import train_with_schedule
from src.metrics.smoothing import smoothed_tail
from src.reporting.ledger import EvidenceLedger
from src.reporting.plots import save_figure
from src.reporting.tables import write_csv, write_json
from src.reporting.markdown_report import write_markdown

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"


def lr_grid(mode: str) -> list[float]:
    n = lr_grid_points(mode)
    return list(np.geomspace(1e-5, 3e-3, n))


def run(execution_mode: str = "full", ledger: EvidenceLedger | None = None) -> dict:
    corpus = TinyCorpus()
    steps = lr_train_steps(execution_mode)
    rows = []
    width_list = lr_widths(execution_mode)

    for width in width_list:
        wrows: list[dict] = []
        for lr in lr_grid(execution_mode):
            n_head = max(4, width // 64)
            while width % n_head != 0:
                n_head -= 1
            cfg = LabConfig(
                model=ModelConfig(seed=1337, width=width, n_head=n_head),
                optimizer=OptimizerConfig(learning_rate=float(lr)),
                schedule=ScheduleConfig(warmup_steps=10, total_steps=steps, stable_steps=20),
                data=DataConfig(batch_size=2),
                runtime=RuntimeConfig(device="cpu", execution_mode=execution_mode),
            )
            t0 = time.perf_counter()
            result = train_with_schedule(cfg, corpus, steps, schedule_name="wsd")
            elapsed = time.perf_counter() - t0
            losses = [s.loss for s in result.steps]
            smooth = smoothed_tail(losses)
            best_i = min(range(len(losses)), key=lambda i: losses[i]) if losses else 0
            row = {
                "width": width,
                "learning_rate": float(lr),
                "seed": 1337,
                "optimizer": "AdamW",
                "schedule": "wsd",
                "warmup_steps": 10,
                "total_steps": steps,
                "initial_loss": losses[0] if losses else float("nan"),
                "final_loss": losses[-1] if losses else float("nan"),
                "smoothed_final_loss": smooth,
                "best_loss": losses[best_i] if losses else float("nan"),
                "best_step": best_i,
                "divergence_flag": result.divergence_flag,
                "nan_flag": result.nan_flag,
                "throughput": steps / max(elapsed, 1e-6),
                "peak_memory_if_available": float("nan"),
                "configuration_hash": cfg.full_hash(),
                "execution_mode": execution_mode,
            }
            rows.append(row)
            wrows.append(row)

        fig, ax = plt.subplots(figsize=(8, 4))
        lrs = [r["learning_rate"] for r in wrows]
        sl = [r["smoothed_final_loss"] for r in wrows]
        ax.semilogx(lrs, sl, "o-", label="smoothed final loss")
        candidates = [r for r in wrows if not r["nan_flag"] and not r["divergence_flag"]]
        if candidates:
            best = min(candidates, key=lambda r: r["smoothed_final_loss"])
            ax.scatter([best["learning_rate"]], [best["smoothed_final_loss"]], color="red", s=120, zorder=5, label="minimum")
            ax.annotate(
                f"min LR={best['learning_rate']:.2e}",
                (best["learning_rate"], best["smoothed_final_loss"]),
                textcoords="offset points",
                xytext=(10, 10),
            )
        ax.set_xlabel("Learning rate")
        ax.set_ylabel("Smoothed final loss")
        ax.set_title(f"LR Sweep width={width} — EXP-LR-001")
        ax.legend()
        save_figure(fig, FIGURES / f"lr_sweep_width_{width}.png")

    write_csv(OUTPUTS / "lr_sweep.csv", rows)
    write_json(OUTPUTS / "lr_sweep.json", rows)

    fig, ax = plt.subplots(figsize=(10, 5))
    mins: dict[int, float] = {}
    min_losses: dict[int, float] = {}
    for width in width_list:
        wrows = [r for r in rows if r["width"] == width]
        ax.semilogx(
            [r["learning_rate"] for r in wrows],
            [r["smoothed_final_loss"] for r in wrows],
            "o-",
            label=f"w={width}",
        )
        candidates = [r for r in wrows if not r["nan_flag"] and not r["divergence_flag"]]
        if candidates:
            best = min(candidates, key=lambda r: r["smoothed_final_loss"])
            mins[width] = best["learning_rate"]
            min_losses[width] = best["smoothed_final_loss"]
            ax.scatter([best["learning_rate"]], [best["smoothed_final_loss"]], s=100, zorder=5)

    ax.set_xlabel("Learning rate")
    ax.set_ylabel("Smoothed final loss")
    ax.legend()
    ax.set_title("LR Sweep Combined — minima marked")
    save_figure(fig, FIGURES / "lr_sweep_combined.png")

    measured_widths = sorted(mins.keys())
    extrap: dict = {"width": 4096, "label": "INFERRED"}
    if len(measured_widths) >= 2:
        lrs_m = [mins[w] for w in measured_widths]
        coeffs = np.polyfit(np.log(measured_widths), np.log(lrs_m), 1)
        proposed = float(np.exp(coeffs[1] + coeffs[0] * math.log(4096)))
        monotonic = all(lrs_m[i] >= lrs_m[i + 1] for i in range(len(lrs_m) - 1)) or all(
            lrs_m[i] <= lrs_m[i + 1] for i in range(len(lrs_m) - 1)
        )
        extrap.update(
            {
                "proposed_learning_rate": proposed,
                "extrapolation_method": "log-log linear fit on measured minima",
                "measured_supporting_points": measured_widths,
                "confidence": "LOW",
                "why_confidence_is_limited": "Width 4096 not measured; tiny corpus; single seed; CPU only",
                "next_validation_sweep": "Run width=4096 at proposed LR ± 0.5 dex",
                "scaling": "MONOTONIC" if monotonic else "NON-MONOTONIC_SCALING",
            }
        )
    else:
        extrap.update(
            {
                "proposed_learning_rate": None,
                "confidence": "LOW",
                "why_confidence_is_limited": "Insufficient measured widths",
            }
        )

    md_lines = [
        "# LR Sweep Decision — EXP-LR-001",
        f"**Execution mode:** {execution_mode}",
        "",
        "## Measured minima (loss vs learning rate)",
        "",
        "| Width | Best LR | Smoothed loss at min | Label |",
        "|------:|--------:|---------------------:|-------|",
    ]
    for w in width_list:
        if w in mins:
            md_lines.append(f"| {w} | {mins[w]:.4e} | {min_losses[w]:.4f} | MEASURED |")
        else:
            md_lines.append(f"| {w} | UNAVAILABLE | UNAVAILABLE | NOT_REACHED |")

    prop = extrap.get("proposed_learning_rate")
    md_lines.extend(
        [
            "",
            "## Width 4096 (NOT MEASURED — INFERRED only)",
            "",
            f"- **Proposed LR:** {prop:.4e} (INFERRED)" if prop else "- **Proposed LR:** UNAVAILABLE",
            f"- **Confidence:** {extrap.get('confidence', 'LOW')} — width 4096 was not run",
            f"- **Method:** {extrap.get('extrapolation_method', 'N/A')}",
            f"- **Scaling:** {extrap.get('scaling', 'N/A')}",
            f"- **Why confidence is limited:** {extrap.get('why_confidence_is_limited', '')}",
        ]
    )
    write_markdown(OUTPUTS / "lr_sweep_decision.md", "\n".join(md_lines))
    write_json(OUTPUTS / "lr_sweep_summary.json", {"min_lr_by_width": mins, "width_4096": extrap, "execution_mode": execution_mode})

    if ledger is not None:
        ledger.append(
            EvidenceLedger.make_record(
                evidence_id="EVD-LR-001",
                experiment_id="EXP-LR-001",
                claim_id="CLAIM-005",
                hypothesis="Optimal LR varies with width",
                controls={"optimizer": "AdamW", "schedule": "wsd", "seed": 1337},
                changed_variable="learning_rate_and_width",
                seed=1337,
                model_config={"widths": width_list},
                optimizer_config={"name": "AdamW"},
                schedule_config={"name": "wsd"},
                data_config={"corpus": "TinyCorpus"},
                runtime_config={"execution_mode": execution_mode},
                raw_artifacts=[
                    "outputs/lr_sweep.csv",
                    "outputs/lr_sweep.json",
                    "outputs/lr_sweep_decision.md",
                    "outputs/lr_sweep_summary.json",
                    "outputs/figures/lr_sweep_combined.png",
                ],
                derived_metrics={
                    "min_lr_by_width": {"value": mins, "label": "MEASURED"},
                    "width_4096": {"value": extrap, "label": "INFERRED"},
                },
                statistical_summary={"n_runs": len(rows), "widths_measured": width_list},
                decision="SUPPORTED" if len(mins) == len(width_list) else "NOT_REACHED",
                confidence="MEDIUM" if len(mins) == len(width_list) else "LOW",
                limitations=["4096 not measured", "Tiny corpus"],
                reproducibility_command=f"python scripts/run_lr_sweep.py --mode {execution_mode}",
                execution_mode=execution_mode,
            )
        )

    return {"min_lr_by_width": mins, "extrapolation_4096": extrap}
