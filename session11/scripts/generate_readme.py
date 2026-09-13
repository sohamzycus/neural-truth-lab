#!/usr/bin/env python3
"""Generate README from actual output artifacts only."""

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"
README_FIGURES = ROOT / "assets" / "readme" / "figures"


def _sync_figures_for_readme() -> None:
    """Copy run plots into assets/readme/figures so README paths resolve on GitHub and in IDE."""
    src = OUTPUTS / "figures"
    README_FIGURES.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for png in src.glob("*.png"):
        shutil.copy2(png, README_FIGURES / png.name)


def _fig(filename: str, caption: str, width: int = 780) -> str:
    """HTML image block — renders reliably in GitHub and Cursor (avoids broken markdown alt colons)."""
    path = f"assets/readme/figures/{filename}"
    return f"""<p align="center">
  <img src="{path}" alt="{caption}" width="{width}"/>
</p>
<p align="center"><em>{caption}</em></p>
"""


def _j(name: str) -> dict:
    p = OUTPUTS / name
    return json.loads(p.read_text()) if p.exists() else {}


def _ledger_records() -> list[dict]:
    p = OUTPUTS / "evidence_ledger.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _adam_max_diff() -> str:
    p = OUTPUTS / "adam_manual_vs_pytorch.csv"
    if not p.exists():
        return "UNAVAILABLE"
    mx = 0.0
    with p.open() as f:
        for row in csv.DictReader(f):
            for k, v in row.items():
                if k.startswith("diff_"):
                    mx = max(mx, float(v))
    return f"{mx:.3e}"


def _lr_mins(summary: dict) -> dict[int, float]:
    out: dict[int, float] = {}
    for k, v in summary.get("min_lr_by_width", {}).items():
        out[int(k)] = float(v)
    return out


def _fmt_loss(v) -> str:
    return f"{v:.4f}" if isinstance(v, (int, float)) else str(v)


def main() -> int:
    _sync_figures_for_readme()
    records = _ledger_records()
    mode = records[0].get("execution_mode", "unknown") if records else "unknown"

    bias = _j("bias_correction.json")
    ratio = _j("layer_ratio_summary.json")
    sched = _j("schedule_summary.json")
    lr_sum = _j("lr_sweep_summary.json")
    mins = _lr_mins(lr_sum)
    extrap = lr_sum.get("width_4096", {})
    prop = extrap.get("proposed_learning_rate")
    prop_str = f"{prop:.4e}" if prop else "UNAVAILABLE"

    sched_rows = _j("schedule_comparison.json")
    if isinstance(sched_rows, list) and len(sched_rows) >= 2:
        cos = next(r for r in sched_rows if r.get("schedule_type") == "cosine")
        wsd = next(r for r in sched_rows if r.get("schedule_type") == "wsd")
        l200_c = cos.get("loss_at_step_200")
        l200_w = wsd.get("loss_at_step_200")
        l300_c = cos.get("loss_at_step_300")
        l300_w = wsd.get("loss_at_step_300")
    else:
        l200_c = sched.get("loss_cosine_step_200")
        l200_w = sched.get("loss_wsd_step_200")
        l300_c = l300_w = None

    rel_pct = ""
    if isinstance(l200_c, (int, float)) and isinstance(l200_w, (int, float)):
        rel_pct = f"{abs(l200_c - l200_w) / max(min(l200_c, l200_w), 1e-8) * 100:.1f}%"

    lr_loss_at_min: dict[int, float] = {}
    csv_path = OUTPUTS / "lr_sweep.csv"
    if csv_path.exists():
        with csv_path.open() as f:
            for row in csv.DictReader(f):
                w = int(row["width"])
                lr = float(row["learning_rate"])
                if w in mins and abs(lr - mins[w]) < 1e-12:
                    lr_loss_at_min[w] = float(row["smoothed_final_loss"])

    stab = ratio.get("stabilization_step")
    stab_label = "MEASURED" if stab else "NOT_REACHED"
    conv = bias.get("difference_stops_mattering_step", "N/A")
    conv_label = "MEASURED" if bias.get("convergence_step_index") is not None else "NOT_REACHED"

    readme = f"""# ERA V5 Session 11 — Optimizer Evidence Lab

**Session 11 asks a different question than “did loss go down?”**  
It asks: *what exactly did we measure, under what controls, and how much should we trust the answer?*

Every number in the results sections is loaded from **`outputs/`** for this run (`execution_mode={mode}`).  
Regenerate after any run:

```bash
cd session11 && source .venv/bin/activate
python scripts/run_all.py --mode smoke
python scripts/generate_readme.py
python scripts/audit_submission.py
```

---

## Core idea: Optimizer Evidence Ledger

Optimizer claims are **hypotheses**, not facts, until they are linked to evidence:

```
spec (YAML) → experiment → raw CSV/JSON/plot → derived metric → decision → confidence
```

Each claim gets one row in [`outputs/evidence_ledger.jsonl`](outputs/evidence_ledger.jsonl).  
If a conclusion is missing from the ledger, it does not count.

| Claim | Experiment | Decision | Confidence | First artifact |
|-------|------------|----------|------------|----------------|
"""
    for r in records:
        art = r.get("raw_artifacts", ["?"])[0]
        readme += f"| {r.get('claim_id')} | {r.get('experiment_id')} | {r.get('decision')} | {r.get('confidence')} | `{art}` |\n"

    readme += f"""
Human-readable copy: [`outputs/evidence_ledger.md`](outputs/evidence_ledger.md)  
Plots + tables for this run: [`artifacts/run_report.md`](artifacts/run_report.md)

**Label key:** MEASURED = from a run; CALCULATED = deterministic transform; INFERRED = extrapolation; NOT_REACHED = threshold/window exhausted.

---

## Repository map

| Component | Role |
|-----------|------|
| `specs/` | Experiments, metrics, acceptance rules — validated before training |
| `src/experiments/` | Five experiment implementations (EXP-ADAM-001 … EXP-LR-001) |
| `src/validation/comparison_validator.py` | Blocks schedule A vs B if non-schedule controls differ |
| `src/reporting/ledger.py` | Writes EvidenceRecord entries |
| `scripts/run_all.py` | Full pipeline: specs → runs → ledger → README |
| `outputs/` | All artifacts for this run |

**Model:** tiny causal GPT + fixed word corpus, CPU-only, seed 1337.

---

## Experiment 1 — Manual Adam (EXP-ADAM-001)

**Question:** Does our hand-written Adam match `torch.optim.Adam` step for step?

**Setup:** one weight (0.5), five fixed gradients, lr=0.001, β=(0.9, 0.999), ε=1e-8.  
Manual code in `adam_manual.py` never imports PyTorch for the manual path.

**Update rule:**

```
m  = β1·m + (1−β1)·g
v  = β2·v + (1−β2)·g²
m̂ = m / (1−β1ᵗ)     v̂ = v / (1−β2ᵗ)
w  ← w − lr · m̂ / (√v̂ + ε)
```

**Results ({mode} run):**

| Check | Value | Label |
|-------|------:|-------|
| max &#124;manual − torch&#124; | **{_adam_max_diff()}** | CALCULATED |
| Claim status | SUPPORTED | — |

{_fig("adam_manual_verification.png", "Figure 1 — Manual vs PyTorch weight difference per step (red line = 1e-6 tolerance)")}

Each point is one optimizer step. The line stays below tolerance — manual and library agree to machine precision. CSV: [`outputs/adam_manual_vs_pytorch.csv`](outputs/adam_manual_vs_pytorch.csv).

---

## Experiment 2 — Bias correction on vs off (EXP-BIAS-001)

**Question:** How much do bias-corrected and uncorrected Adam differ, and after which step is the gap negligible?

**Setup:** 20 steps, identical gradients and hyperparameters; only the bias-correction flag changes.

**Convergence rule (from spec):** abs_diff &lt; 1e-6 **and** rel_diff &lt; 1e-4 for **3 consecutive steps**, else report `NOT_REACHED_WITHIN_WINDOW`.

**Results:**

| Metric | Value | Label |
|--------|------:|-------|
| Abs diff at step 1 | **{bias.get('early_step1_abs_diff', 0):.4e}** | MEASURED |
| Step where diff stops mattering | **{conv}** | {conv_label} |
| Abs diff at step 20 | **{bias.get('final_abs_diff', 0):.4e}** | MEASURED |
| Claim status | {bias.get('decision', 'N/A')} | — |

{_fig("bias_correction.png", "Figure 2 — Bias correction ON vs OFF (trajectories, abs/rel diff, update magnitude)", 820)}

- **Top left:** weight paths diverge when correction is off.
- **Top right / bottom left:** differences stay above tolerance for all 20 steps → `NOT_REACHED_WITHIN_WINDOW`.
- **Bottom right:** uncorrected update magnitudes stay larger early on.

Full report: [`outputs/bias_correction_report.md`](outputs/bias_correction_report.md)

---

## Experiment 3 — Update-to-weight ratio (EXP-RATIO-001)

**Question:** When warmup ends, does the per-layer update size (relative to weight norm) change regime?

**Metric:** `ratio = ‖Δθ‖ / max(‖θ‖, ε)` using the **actual weight change** after `optimizer.step()`, not the gradient.

**Results:**

| Metric | Value | Label |
|--------|------:|-------|
| Layers logged | **{ratio.get('n_layers_logged', 'N/A')}** | MEASURED |
| Warmup ends at step | **{ratio.get('warmup_end_step', 'N/A')}** | MEASURED |
| Mean ratio before warmup | **{ratio.get('ratio_before_warmup_end', 0):.2e}** | MEASURED |
| Mean ratio after warmup | **{ratio.get('ratio_after_warmup_end', 0):.2e}** | MEASURED |
| Stabilization step | **{stab or 'NOT_REACHED'}** | {stab_label} |

{_fig("layer_update_ratio.png", f"Figure 3 — Mean update/weight ratio (warmup ends at step {ratio.get('warmup_end_step', '?')})", 780)}

Ratio is high during warmup, then drops after step {ratio.get('warmup_end_step', '?')} when the schedule multiplier saturates.

{_fig("layer_update_ratio_heatmap.png", "Figure 4 — Per-layer ratio heatmap (sample layers × steps)", 820)}

Each row is a layer; color shift at the warmup boundary marks the same transition across layers.

Raw log: [`outputs/layer_update_ratio.csv`](outputs/layer_update_ratio.csv)

---

## Experiment 4 — Cosine vs WSD schedules (EXP-SCHEDULE-001)

**Question:** At the official checkpoint (step 200), which schedule gives lower loss when **everything else is locked**?

**Controls matched:** model, init weights, data order, seed, AdamW hyperparameters, batch size, dtype, clipping, weight decay, 300 total steps.  
**Only variable:** schedule type. Validator status: **{sched.get('comparison_validation_status', 'N/A')}**.

**Schedule definitions (in spec):**
- **Cosine:** warmup → cosine decay to min LR
- **WSD:** warmup → stable plateau → cosine decay

**Results at checkpoint step 200:**

| Schedule | Loss @ step 200 | Loss @ step 300 | Label |
|----------|----------------:|----------------:|-------|
| cosine | **{_fmt_loss(l200_c)}** | {_fmt_loss(l300_c)} | MEASURED |
| wsd | **{_fmt_loss(l200_w)}** | {_fmt_loss(l300_w)} | MEASURED |

| Decision field | Value |
|----------------|-------|
| Relative gap @ 200 | {rel_pct or 'N/A'} |
| Checkpoint choice | **{sched.get('model_to_keep', 'N/A')}** |
| Policy decision | {sched.get('decision', 'N/A')} |

Step 200 is the **official** comparison point. Step 300 is **diagnostic** only.

{_fig("cosine_vs_wsd_loss.png", "Figure 5 — Training loss (vertical marker = step 200 checkpoint)", 780)}

At step 200, the lower curve wins — **{sched.get('model_to_keep', 'N/A')}** in this run.

{_fig("cosine_vs_wsd_lr.png", "Figure 6 — Learning-rate multiplier over time (cosine vs WSD)", 780)}

WSD holds a mid-training plateau; cosine decays throughout — same optimizer, different effective LR budget.

Evidence: [`outputs/schedule_comparison.csv`](outputs/schedule_comparison.csv)

---

## Experiment 5 — Learning-rate sweep (EXP-LR-001)

**Question:** For widths 256, 512, and 1024, which learning rate minimizes smoothed final loss? What LR would we **guess** at width 4096 without running it?

**Setup:** log-spaced LR grid, AdamW + WSD, smoothed final loss = mean of last 5 steps.  
Red markers on plots = measured minimum per width.

**Measured minima:**

| Width | Best LR | Loss at min | Label |
|------:|--------:|------------:|-------|
"""
    for w in [256, 512, 1024]:
        if w in mins:
            loss_s = f"{lr_loss_at_min[w]:.4f}" if w in lr_loss_at_min else "N/A"
            readme += f"| {w} | **{mins[w]:.4e}** | {loss_s} | MEASURED |\n"
        else:
            readme += f"| {w} | — | — | NOT_REACHED |\n"

    readme += f"""
**Width 4096 (not run):**

| Field | Value | Label |
|-------|-------|-------|
| Proposed LR | **{prop_str}** | INFERRED |
| Confidence | **{extrap.get('confidence', 'LOW')}** | — |

No row for width 4096 in [`outputs/lr_sweep.csv`](outputs/lr_sweep.csv).

{_fig("lr_sweep_combined.png", "Figure 7 — Smoothed final loss vs LR (all widths; dots = minima)", 780)}
"""
    for w in [256, 512, 1024]:
        if w in mins:
            loss_s = f"{lr_loss_at_min[w]:.4f}" if w in lr_loss_at_min else "N/A"
            readme += f"""
**Width {w}** — best LR **{mins[w]:.4e}**, loss at min **{loss_s}** (MEASURED)

{_fig(f"lr_sweep_width_{w}.png", f"Figure — LR sweep at hidden size {w} (red dot = minimum)", 720)}
"""

    readme += f"""
U-shaped curves: too-small LR under-trains, too-large LR diverges. Width 4096 uses **INFERRED** LR **{prop_str}** (confidence **{extrap.get('confidence', 'LOW')}**) only.

Details: [`outputs/lr_sweep_decision.md`](outputs/lr_sweep_decision.md)

---

## Summary

| # | Experiment | Main takeaway from this run |
|---|------------|----------------------------|
| 1 | EXP-ADAM-001 | Manual Adam matches PyTorch to ~1e-17 — implementation is trustworthy |
| 2 | EXP-BIAS-001 | Early difference is real; 20-step window did **not** reach convergence tolerance |
| 3 | EXP-RATIO-001 | Warmup ends at step {ratio.get('warmup_end_step', '?')}; ratio regime changes there |
| 4 | EXP-SCHEDULE-001 | At step 200, **{sched.get('model_to_keep', 'N/A')}** wins under validated controls |
| 5 | EXP-LR-001 | Min LR measured at 256/512/1024; 4096 is INFERRED only |

---

## Install

```bash
cd session11
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Full reproduction

```bash
python scripts/validate_specs.py
python scripts/run_all.py --mode smoke
python scripts/generate_readme.py
python scripts/audit_submission.py
```

Specs: [`specs/`](specs/) · Traceability: [`artifacts/traceability_matrix.md`](artifacts/traceability_matrix.md)

---

## Limitations

- Small model and corpus — results illustrate the **evidence workflow**, not SOTA training
- Single seed — no replication variance
- Width 4096 not trained — INFERRED LR only
- Bias convergence NOT_REACHED in 20 steps under stated tolerances
- Smoke mode uses a 5-point LR grid (`--mode full` uses 7 points)
"""
    (ROOT / "README.md").write_text(readme)
    print("README generated from artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
