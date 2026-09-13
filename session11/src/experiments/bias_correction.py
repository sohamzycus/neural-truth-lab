"""EXP-BIAS-001 — Bias correction investigation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from src.core.mode_config import bias_steps
from src.optimizers.adam_manual import adam_manual_steps
from src.metrics.convergence import find_convergence_step
from src.reporting.ledger import EvidenceLedger
from src.reporting.plots import save_figure
from src.reporting.tables import write_json
from src.reporting.markdown_report import write_markdown

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"

GRADIENTS = [
    0.1, -0.2, 0.05, 0.3, -0.1, 0.15, -0.05, 0.2, -0.15, 0.1,
    -0.1, 0.05, -0.2, 0.1, 0.3, -0.05, 0.2, -0.1, 0.05, -0.15,
]
ABS_TOL = 1e-6
REL_TOL = 1e-4
CONSEC = 3


def run(execution_mode: str = "full", ledger: EvidenceLedger | None = None) -> dict:
    n_steps = bias_steps(execution_mode)
    grads = GRADIENTS[:n_steps]

    with_bias = adam_manual_steps(0.5, grads, bias_correction=True)
    no_bias = adam_manual_steps(0.5, grads, bias_correction=False)

    weights_on = [r.updated_weight for r in with_bias]
    weights_off = [r.updated_weight for r in no_bias]
    abs_diffs = [abs(a - b) for a, b in zip(weights_on, weights_off)]
    rel_diffs = [ad / max(abs(a), abs(b), 1e-8) for a, b, ad in zip(weights_on, weights_off, abs_diffs)]
    update_mag_on = [abs(r.signed_step) for r in with_bias]
    update_mag_off = [abs(r.signed_step) for r in no_bias]

    conv_idx = find_convergence_step(abs_diffs, rel_diffs, ABS_TOL, REL_TOL, CONSEC)
    if conv_idx is not None:
        stops_mattering_step = conv_idx + 1  # 1-indexed step number
        conv_label = stops_mattering_step
    else:
        stops_mattering_step = None
        conv_label = "NOT_REACHED_WITHIN_WINDOW"

    early_step1_abs = abs_diffs[0]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    steps = list(range(1, n_steps + 1))
    axes[0, 0].plot(steps, weights_on, label="bias correction ON")
    axes[0, 0].plot(steps, weights_off, label="bias correction OFF")
    axes[0, 0].set_title("Parameter trajectory (20 steps)")
    axes[0, 0].legend()
    axes[0, 1].plot(steps, abs_diffs)
    axes[0, 1].axhline(ABS_TOL, color="r", ls="--", label=f"abs_tol={ABS_TOL}")
    axes[0, 1].set_title("Absolute difference")
    axes[0, 1].legend()
    axes[1, 0].plot(steps, rel_diffs)
    axes[1, 0].axhline(REL_TOL, color="r", ls="--", label=f"rel_tol={REL_TOL}")
    axes[1, 0].set_title("Relative difference")
    axes[1, 0].legend()
    axes[1, 1].plot(steps, update_mag_on, label="with bias")
    axes[1, 1].plot(steps, update_mag_off, label="without bias")
    axes[1, 1].set_title("Update magnitude")
    axes[1, 1].legend()
    for ax in axes.flat:
        ax.set_xlabel("Step")
    fig.suptitle("EXP-BIAS-001: Adam with vs without bias correction", fontsize=11)
    fig.tight_layout()
    save_figure(fig, FIGURES / "bias_correction.png")

    # Early effect measured; convergence may be NOT_REACHED (honest)
    early_supported = early_step1_abs > 0
    if conv_idx is not None:
        decision = "SUPPORTED"
        confidence = "MEDIUM"
    elif early_supported:
        decision = "NOT_REACHED"
        confidence = "LOW"
    else:
        decision = "REFUTED"
        confidence = "HIGH"

    result = {
        "execution_mode": execution_mode,
        "steps": n_steps,
        "early_step1_abs_diff": early_step1_abs,
        "early_effect_measured": early_supported,
        "difference_stops_mattering_step": conv_label,
        "convergence_step_index": conv_idx,
        "absolute_tolerance": ABS_TOL,
        "relative_tolerance": REL_TOL,
        "consecutive_steps_required": CONSEC,
        "final_abs_diff": abs_diffs[-1],
        "final_rel_diff": rel_diffs[-1],
        "decision": decision,
        "confidence": confidence,
    }
    write_json(OUTPUTS / "bias_correction.json", result)

    md = f"""# Bias Correction Report — EXP-BIAS-001

**Execution mode:** {execution_mode}

| Metric | Value | Label |
|--------|------:|-------|
| Steps plotted | {n_steps} | MEASURED |
| Early abs diff (step 1) | {early_step1_abs:.6e} | MEASURED |
| Difference stops mattering at step | {conv_label} | {'MEASURED' if conv_idx is not None else 'NOT_REACHED'} |
| Final abs diff (step {n_steps}) | {abs_diffs[-1]:.6e} | MEASURED |

Policy: abs_tol={ABS_TOL}, rel_tol={REL_TOL}, consecutive={CONSEC}.

**Decision:** {decision} (early effect {'yes' if early_supported else 'no'}; convergence {conv_label})
"""
    write_markdown(OUTPUTS / "bias_correction_report.md", md)

    if ledger is not None:
        ledger.append(
            EvidenceLedger.make_record(
                evidence_id="EVD-BIAS-001",
                experiment_id="EXP-BIAS-001",
                claim_id="CLAIM-002",
                hypothesis="Bias correction measurably changes early updates",
                controls={"same_grads": True, "same_hyperparams": True, "steps": n_steps},
                changed_variable="bias_correction",
                seed=0,
                model_config={},
                optimizer_config={"lr": 0.001, "bias_correction": "on vs off"},
                schedule_config={},
                data_config={},
                runtime_config={"execution_mode": execution_mode},
                raw_artifacts=[
                    "outputs/bias_correction.json",
                    "outputs/bias_correction_report.md",
                    "outputs/figures/bias_correction.png",
                ],
                derived_metrics={
                    "early_step1_abs_diff": {"value": early_step1_abs, "label": "MEASURED"},
                    "difference_stops_mattering_step": {"value": conv_label, "label": "MEASURED" if conv_idx is not None else "NOT_REACHED"},
                },
                statistical_summary=result,
                decision=decision,
                confidence=confidence,
                limitations=["Scalar weight; convergence may not occur within 20 steps"],
                reproducibility_command=f"python scripts/run_bias_correction.py --mode {execution_mode}",
                execution_mode=execution_mode,
            )
        )

    return result
