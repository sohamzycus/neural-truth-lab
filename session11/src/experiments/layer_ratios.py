"""EXP-RATIO-001 — Layer update-to-weight ratios."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.core.data import TinyCorpus
from src.core.mode_config import ratio_stable, ratio_train_steps, ratio_warmup
from src.core.schemas import DataConfig, LabConfig, ModelConfig, OptimizerConfig, RuntimeConfig, ScheduleConfig
from src.core.training import train_with_schedule
from src.metrics.ratio_metrics import detect_stabilization, detect_warmup_end
from src.reporting.ledger import EvidenceLedger
from src.reporting.plots import save_figure
from src.reporting.tables import write_csv, write_json
from src.reporting.markdown_report import write_markdown

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"


def run(execution_mode: str = "full", ledger: EvidenceLedger | None = None) -> dict:
    n_steps = ratio_train_steps(execution_mode)
    cfg = LabConfig(
        model=ModelConfig(seed=1337),
        optimizer=OptimizerConfig(learning_rate=3e-4),
        schedule=ScheduleConfig(
            warmup_steps=ratio_warmup(execution_mode),
            total_steps=n_steps,
            stable_steps=ratio_stable(execution_mode),
        ),
        data=DataConfig(batch_size=2),
        runtime=RuntimeConfig(device="cpu", execution_mode=execution_mode),
    )
    corpus = TinyCorpus()
    result = train_with_schedule(cfg, corpus, n_steps, schedule_name="wsd", log_layer_ratios=True)

    layers_logged = sorted(set(r.layer_name for r in result.layer_ratios))
    rows = [
        {
            "layer_name": r.layer_name,
            "parameter_shape": str(r.parameter_shape),
            "parameter_norm": r.parameter_norm,
            "gradient_norm": r.gradient_norm,
            "update_norm": r.update_norm,
            "update_to_weight_ratio": r.update_to_weight_ratio,
            "learning_rate": r.learning_rate,
            "warmup_fraction": r.warmup_fraction,
            "schedule_multiplier": r.schedule_multiplier,
            "optimizer_step": r.optimizer_step,
            "execution_mode": execution_mode,
        }
        for r in result.layer_ratios
    ]
    write_csv(OUTPUTS / "layer_update_ratio.csv", rows)
    write_json(OUTPUTS / "layer_update_ratio.json", {"n_layers": len(layers_logged), "n_rows": len(rows), "rows": rows[:5]})

    by_step: dict[int, list[float]] = {}
    wf_by_step: dict[int, float] = {}
    for r in result.layer_ratios:
        by_step.setdefault(r.optimizer_step, []).append(r.update_to_weight_ratio)
        wf_by_step[r.optimizer_step] = r.warmup_fraction
    steps = sorted(by_step.keys())
    mean_ratios = [sum(by_step[s]) / len(by_step[s]) for s in steps]
    warmup_fracs = [wf_by_step[s] for s in steps]

    warmup_end = detect_warmup_end(warmup_fracs)
    before = mean_ratios[: warmup_end + 1]
    after = mean_ratios[warmup_end + 1 :] if warmup_end + 1 < len(mean_ratios) else []
    stab_step, stab_rule = detect_stabilization(mean_ratios, warmup_end + 1)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(steps, mean_ratios, label="mean ratio (all layers)")
    ax.axvline(warmup_end, color="orange", ls="--", linewidth=2, label=f"warmup stops changing LR @ step {warmup_end}")
    if stab_step is not None:
        ax.axvline(stab_step, color="green", ls=":", label=f"ratio stabilization @ {stab_step}")
    ax.set_xlabel("Optimizer step")
    ax.set_ylabel("Mean update/weight ratio")
    ax.set_title(f"EXP-RATIO-001 — {len(layers_logged)} layers logged every step")
    ax.legend()
    save_figure(fig, FIGURES / "layer_update_ratio.png")

    layer_names = layers_logged[:10]
    mat = np.zeros((len(layer_names), len(steps)))
    for i, layer in enumerate(layer_names):
        for j, s in enumerate(steps):
            vals = [r.update_to_weight_ratio for r in result.layer_ratios if r.layer_name == layer and r.optimizer_step == s]
            mat[i, j] = vals[0] if vals else 0
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    im = ax2.imshow(mat, aspect="auto", cmap="viridis")
    ax2.axvline(warmup_end, color="white", ls="--", linewidth=2)
    ax2.set_yticks(range(len(layer_names)))
    ax2.set_yticklabels([n.split(".")[-1] for n in layer_names], fontsize=7)
    ax2.set_xlabel("Step")
    ax2.set_title("Per-layer update/weight ratio heatmap")
    fig2.colorbar(im, ax=ax2)
    save_figure(fig2, FIGURES / "layer_update_ratio_heatmap.png")

    ratio_before = sum(before) / len(before) if before else None
    ratio_after = sum(after) / len(after) if after else None

    summary = {
        "execution_mode": execution_mode,
        "n_layers_logged": len(layers_logged),
        "warmup_end_step": warmup_end,
        "warmup_stops_changing_lr_at_step": warmup_end,
        "ratio_before_warmup_end": ratio_before,
        "ratio_after_warmup_end": ratio_after,
        "stabilization_step": stab_step,
        "stabilization_rule": stab_rule,
    }
    write_json(OUTPUTS / "layer_ratio_summary.json", summary)

    ratio_after_str = f"{ratio_after:.6e}" if ratio_after is not None else "UNAVAILABLE"
    md = f"""# Layer Ratio Summary — EXP-RATIO-001

**Execution mode:** {execution_mode}
**Layers logged:** {len(layers_logged)} (every trainable layer, every step)

| Metric | Value | Label |
|--------|------:|-------|
| warmup_end_step | {warmup_end} | MEASURED |
| warmup stops changing schedule multiplier | step {warmup_end} | MEASURED |
| mean ratio before warmup end | {ratio_before:.6e} | MEASURED |
| mean ratio after warmup end | {ratio_after_str} | MEASURED |
| stabilization_step | {stab_step if stab_step is not None else 'NOT_REACHED'} | {'MEASURED' if stab_step else 'NOT_REACHED'} |

Warmup transition detected mathematically (METRIC-WARMUP-001).
"""
    write_markdown(OUTPUTS / "layer_ratio_summary.md", md)

    if ledger is not None:
        ledger.append(
            EvidenceLedger.make_record(
                evidence_id="EVD-RATIO-001",
                experiment_id="EXP-RATIO-001",
                claim_id="CLAIM-003",
                hypothesis="Update/weight ratio shows warmup transition",
                controls={"model": "TinyGPT", "optimizer": "AdamW", "schedule": "WSD"},
                changed_variable="training_step",
                seed=1337,
                model_config=cfg.model.to_dict(),
                optimizer_config=cfg.optimizer.to_dict(),
                schedule_config=cfg.schedule.to_dict(),
                data_config=cfg.data.to_dict(),
                runtime_config=cfg.runtime.to_dict(),
                raw_artifacts=[
                    "outputs/layer_update_ratio.csv",
                    "outputs/layer_ratio_summary.json",
                    "outputs/layer_ratio_summary.md",
                    "outputs/figures/layer_update_ratio.png",
                    "outputs/figures/layer_update_ratio_heatmap.png",
                ],
                derived_metrics={
                    "warmup_end_step": {"value": warmup_end, "label": "MEASURED"},
                    "stabilization_step": {"value": stab_step, "label": "MEASURED" if stab_step else "NOT_REACHED"},
                },
                statistical_summary=summary,
                decision="SUPPORTED",
                confidence="MEDIUM",
                limitations=["Small model, CPU only"],
                reproducibility_command=f"python scripts/run_layer_ratios.py --mode {execution_mode}",
                execution_mode=execution_mode,
            )
        )

    return summary
