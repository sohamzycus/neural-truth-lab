"""EXP-ADAM-001 — Manual Adam vs PyTorch."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from src.optimizers.adam_manual import adam_manual_steps
from src.optimizers.adam_reference import adam_pytorch_steps
from src.reporting.ledger import EvidenceLedger, apply_decision_policy
from src.reporting.plots import save_figure
from src.reporting.tables import write_csv, write_json
from src.reporting.markdown_report import write_markdown

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"

DEFAULT = {
    "initial_weight": 0.5,
    "gradients": [0.1, -0.2, 0.05, 0.3, -0.1],
    "learning_rate": 0.001,
    "beta1": 0.9,
    "beta2": 0.999,
    "epsilon": 1e-8,
    "weight_decay": 0.0,
}


def run(execution_mode: str = "full", ledger: EvidenceLedger | None = None) -> dict:
    manual = adam_manual_steps(**DEFAULT)
    pytorch = adam_pytorch_steps(**DEFAULT)

    manual_rows = [
        {
            "step": r.step,
            "gradient": r.gradient,
            "m_t": r.m_t,
            "v_t": r.v_t,
            "m_hat_t": r.m_hat_t,
            "v_hat_t": r.v_hat_t,
            "signed_step": r.signed_step,
            "updated_weight": r.updated_weight,
            "execution_mode": execution_mode,
        }
        for r in manual
    ]

    compare_rows = []
    max_diff = 0.0
    fields = ["m_t", "v_t", "m_hat_t", "v_hat_t", "signed_step", "updated_weight"]
    for m, p in zip(manual, pytorch):
        row = {"step": m.step, "execution_mode": execution_mode}
        for f in fields:
            mv = getattr(m, f)
            pv = p[f]
            diff = abs(mv - pv)
            max_diff = max(max_diff, diff)
            row[f"manual_{f}"] = mv
            row[f"pytorch_{f}"] = pv
            row[f"diff_{f}"] = diff
        compare_rows.append(row)

    write_csv(OUTPUTS / "adam_manual_table.csv", manual_rows)
    write_json(OUTPUTS / "adam_manual_table.json", manual_rows)
    write_csv(OUTPUTS / "adam_manual_vs_pytorch.csv", compare_rows)

    status, confidence = apply_decision_policy(
        controls_valid=True, result_missing=False, max_abs_diff=max_diff
    )

    md = [
        "# Adam Manual Verification — EXP-ADAM-001",
        "",
        f"**Execution mode:** {execution_mode}",
        f"**Max absolute difference:** {max_diff:.2e} (CALCULATED)",
        f"**Decision:** {status.value}",
        f"**Confidence:** {confidence}",
        "",
        "All values compared: m_t, v_t, m_hat_t, v_hat_t, signed_step, updated_weight.",
    ]
    write_markdown(OUTPUTS / "adam_manual_verification.md", "\n".join(md))

    fig, ax = plt.subplots(figsize=(8, 4))
    steps = [r["step"] for r in compare_rows]
    diffs = [r["diff_updated_weight"] for r in compare_rows]
    ax.plot(steps, diffs, "o-", label="|weight diff|")
    ax.axhline(1e-6, color="r", ls="--", label="threshold 1e-6")
    if all(d > 0 for d in diffs):
        ax.set_yscale("log")
    ax.set_xlabel("Step")
    ax.set_ylabel("Absolute difference")
    ax.set_title("Manual Adam vs PyTorch")
    ax.legend()
    save_figure(fig, FIGURES / "adam_manual_verification.png")

    artifacts = [
        "outputs/adam_manual_table.csv",
        "outputs/adam_manual_table.json",
        "outputs/adam_manual_vs_pytorch.csv",
        "outputs/adam_manual_verification.md",
        "outputs/figures/adam_manual_verification.png",
    ]

    if ledger is not None:
        ledger.append(
            EvidenceLedger.make_record(
                evidence_id="EVD-ADAM-001",
                experiment_id="EXP-ADAM-001",
                claim_id="CLAIM-001",
                hypothesis="Manual Adam matches PyTorch",
                controls={"fixed_scalar": True, **DEFAULT},
                changed_variable="none",
                seed=0,
                model_config={},
                optimizer_config=DEFAULT,
                schedule_config={},
                data_config={},
                runtime_config={"execution_mode": execution_mode},
                raw_artifacts=artifacts,
                derived_metrics={"max_abs_diff": max_diff, "label": "CALCULATED"},
                statistical_summary={"steps": len(manual)},
                decision=status.value,
                confidence=confidence,
                limitations=["Scalar only, no weight decay"],
                reproducibility_command="python scripts/run_adam_verification.py",
                execution_mode=execution_mode,
            )
        )

    return {"max_abs_diff": max_diff, "decision": status.value, "artifacts": artifacts}
