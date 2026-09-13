#!/usr/bin/env python3
"""Graphical run report from actual outputs — no fabricated numbers."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"
ARTIFACTS = ROOT / "artifacts"


def _j(name: str) -> dict:
    p = OUTPUTS / name
    return json.loads(p.read_text()) if p.exists() else {}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="smoke")
    args = p.parse_args()

    bias = _j("bias_correction.json")
    sched = _j("schedule_summary.json")
    ratio = _j("layer_ratio_summary.json")
    lr = _j("lr_sweep_summary.json")
    adam_md = (OUTPUTS / "adam_manual_verification.md").read_text() if (OUTPUTS / "adam_manual_verification.md").exists() else ""

    ledger_mode = args.mode
    lp = OUTPUTS / "evidence_ledger.jsonl"
    if lp.exists():
        modes = {json.loads(line).get("execution_mode") for line in lp.read_text().splitlines() if line.strip()}
        ledger_mode = ", ".join(sorted(modes))

    extrap = lr.get("width_4096", {})
    prop = extrap.get("proposed_learning_rate")

    report = f"""# Session 11 Graphical Run Report

**Pipeline mode:** `{args.mode}`  
**Ledger execution_mode(s):** `{ledger_mode}`  
**Generated from:** `outputs/` artifacts only

---

## Evidence chain (novelty)

Each row: **Claim → Experiment → Raw file → Metric → Decision**

| Claim | Experiment | Evidence file | Decision |
|-------|------------|---------------|----------|
| CLAIM-001 | EXP-ADAM-001 | `outputs/adam_manual_vs_pytorch.csv` | see ledger |
| CLAIM-002 | EXP-BIAS-001 | `outputs/bias_correction.json` | {bias.get('decision', 'N/A')} |
| CLAIM-003 | EXP-RATIO-001 | `outputs/layer_update_ratio.csv` | see ledger |
| CLAIM-004 | EXP-SCHEDULE-001 | `outputs/schedule_comparison.csv` | {sched.get('decision', 'N/A')} |
| CLAIM-005 | EXP-LR-001 | `outputs/lr_sweep.csv` | see ledger |

Full ledger: `outputs/evidence_ledger.jsonl`

---

## EXP-ADAM-001 — Manual Adam

![Adam verification](../outputs/figures/adam_manual_verification.png)

{adam_md}

---

## EXP-BIAS-001 — Bias correction (20 steps, ON vs OFF)

![Bias correction](../outputs/figures/bias_correction.png)

| Metric | Value | Label |
|--------|------:|-------|
| Early abs diff step 1 | {bias.get('early_step1_abs_diff', 'N/A')} | MEASURED |
| Difference stops mattering at step | {bias.get('difference_stops_mattering_step', 'N/A')} | {'MEASURED' if bias.get('convergence_step_index') is not None else 'NOT_REACHED'} |
| Final abs diff | {bias.get('final_abs_diff', 'N/A')} | MEASURED |

---

## EXP-RATIO-001 — Update/weight ratio (every layer)

![Layer ratio](../outputs/figures/layer_update_ratio.png)

![Heatmap](../outputs/figures/layer_update_ratio_heatmap.png)

| Metric | Value | Label |
|--------|------:|-------|
| Layers logged | {ratio.get('n_layers_logged', 'N/A')} | MEASURED |
| Warmup stops changing LR at step | {ratio.get('warmup_end_step', 'N/A')} | MEASURED |
| Stabilization step | {ratio.get('stabilization_step', 'NOT_REACHED')} | {'MEASURED' if ratio.get('stabilization_step') else 'NOT_REACHED'} |

---

## EXP-SCHEDULE-001 — Cosine vs WSD (300 steps, compare @ 200)

![Loss](../outputs/figures/cosine_vs_wsd_loss.png)

![LR schedule](../outputs/figures/cosine_vs_wsd_lr.png)

| Schedule | Loss @ step 200 | Label |
|----------|----------------:|-------|
| cosine | {sched.get('loss_cosine_step_200', 'N/A')} | MEASURED |
| wsd | {sched.get('loss_wsd_step_200', 'N/A')} | MEASURED |

**Model I would keep:** {sched.get('model_to_keep', 'N/A')} (CALCULATED from step-200 loss under validated controls)

---

## EXP-LR-001 — LR sweep (widths 256, 512, 1024)

![Combined sweep](../outputs/figures/lr_sweep_combined.png)

![w=256](../outputs/figures/lr_sweep_width_256.png)

![w=512](../outputs/figures/lr_sweep_width_512.png)

![w=1024](../outputs/figures/lr_sweep_width_1024.png)

### Measured minima

| Width | Best LR | Label |
|------:|--------:|-------|
"""
    mins = lr.get("min_lr_by_width", {})
    for w in [256, 512, 1024]:
        if w in mins:
            report += f"| {w} | {mins[w]:.4e} | MEASURED |\n"
        else:
            report += f"| {w} | NOT RUN | NOT_REACHED |\n"

    prop_str = f"{prop:.4e}" if prop else "UNAVAILABLE"
    report += f"""
### Width 4096 (INFERRED — not measured)

| Field | Value |
|-------|-------|
| Proposed LR | {prop_str} (INFERRED) |
| Confidence | {extrap.get('confidence', 'LOW')} |
| Method | {extrap.get('extrapolation_method', 'N/A')} |

---

## Reproduce this report

```bash
cd session11 && source .venv/bin/activate
python scripts/run_all.py --mode {args.mode}
python scripts/audit_submission.py
```
"""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "run_report.md").write_text(report)
    print(f"Run report written to artifacts/run_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
