#!/usr/bin/env python3
"""Strict submission audit — Session 11."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"


def check(name: str, ok: bool, detail: str = "") -> tuple[str, bool]:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    return line, ok


def main() -> int:
    lines = ["SESSION 11 OPTIMIZER EVIDENCE LAB AUDIT", ""]
    all_ok = True

    proc = subprocess.run([sys.executable, "scripts/validate_specs.py"], cwd=ROOT, capture_output=True, text=True)
    line, ok = check("specification validation", proc.returncode == 0)
    lines.append(line)
    all_ok &= ok

    adam_csv = OUTPUTS / "adam_manual_vs_pytorch.csv"
    if adam_csv.exists():
        max_diff = 0.0
        with adam_csv.open() as f:
            for row in csv.DictReader(f):
                for k, v in row.items():
                    if k.startswith("diff_"):
                        max_diff = max(max_diff, float(v))
        line, ok = check("manual Adam verification", max_diff < 1e-6, f"max_diff={max_diff:.2e}")
    else:
        line, ok = check("manual Adam verification", False, "missing csv")
    lines.append(line)
    all_ok &= ok

    bias = {}
    if (OUTPUTS / "bias_correction.json").exists():
        bias = json.loads((OUTPUTS / "bias_correction.json").read_text())
    bias_ok = (OUTPUTS / "bias_correction.json").exists() and (OUTPUTS / "figures/bias_correction.png").exists()
    bias_ok &= bias.get("steps") == 20
    line, ok = check("bias correction", bias_ok, f"stops_mattering={bias.get('difference_stops_mattering_step')}")
    lines.append(line)
    all_ok &= ok

    ratio_ok = (OUTPUTS / "layer_update_ratio.csv").exists() and (OUTPUTS / "layer_ratio_summary.md").exists()
    nrows = 0
    if ratio_ok:
        with (OUTPUTS / "layer_update_ratio.csv").open() as f:
            nrows = sum(1 for _ in csv.DictReader(f))
        ratio_ok = nrows > 0
    line, ok = check("update-to-weight logging", ratio_ok, f"rows={nrows if ratio_ok else 0}")
    lines.append(line)
    all_ok &= ok

    sched = {}
    sched_ok = (OUTPUTS / "schedule_comparison.csv").exists() and (OUTPUTS / "schedule_decision.md").exists()
    if sched_ok:
        sched = json.loads((OUTPUTS / "schedule_summary.json").read_text()) if (OUTPUTS / "schedule_summary.json").exists() else {}
        sched_ok = sched.get("comparison_validation_status") == "VALID"
        line, ok = check("cosine vs WSD", sched_ok, f"keep={sched.get('model_to_keep')}")
    else:
        line, ok = check("cosine vs WSD", False, "missing outputs")
    lines.append(line)
    all_ok &= ok

    lr_ok = (OUTPUTS / "lr_sweep.csv").exists() and (OUTPUTS / "lr_sweep_decision.md").exists()
    if lr_ok:
        with (OUTPUTS / "lr_sweep.csv").open() as f:
            widths = {int(r["width"]) for r in csv.DictReader(f)}
        lr_ok = {256, 512, 1024} <= widths and 4096 not in widths
        line, ok = check("learning-rate sweep", lr_ok, f"widths={sorted(widths)}")
    else:
        line, ok = check("learning-rate sweep", False, "missing outputs")
    lines.append(line)
    all_ok &= ok

    ledger_ok = (OUTPUTS / "evidence_ledger.jsonl").exists() and (OUTPUTS / "evidence_ledger.md").exists()
    if ledger_ok:
        records = [json.loads(l) for l in (OUTPUTS / "evidence_ledger.jsonl").read_text().splitlines() if l.strip()]
        modes = {r.get("execution_mode") for r in records}
        claims = {r.get("claim_id") for r in records}
        ledger_ok = len(modes) == 1 and {"CLAIM-001", "CLAIM-002", "CLAIM-003", "CLAIM-004", "CLAIM-005"} <= claims
        line, ok = check("evidence ledger", ledger_ok, f"{len(records)} records, mode={modes.pop() if modes else '?'}")
    else:
        line, ok = check("evidence ledger", False)
    lines.append(line)
    all_ok &= ok

    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, capture_output=True, text=True, timeout=300)
    line, ok = check("tests", proc.returncode == 0, proc.stdout.strip().split("\n")[-1] if proc.stdout else proc.stderr[:100])
    lines.append(line)
    all_ok &= ok

    readme_path = ROOT / "README.md"
    readme_ok = readme_path.exists() and "evidence_ledger.jsonl" in readme_path.read_text()
    if readme_ok and sched:
        readme_ok = str(sched.get("loss_cosine_step_200", "")) in readme_path.read_text() or "N/A" in readme_path.read_text()
    line, ok = check("README", readme_ok)
    lines.append(line)
    all_ok &= ok

    repro_ok = all((ROOT / "scripts" / s).exists() for s in ["validate_specs.py", "run_all.py", "generate_readme.py", "audit_submission.py"])
    line, ok = check("reproducibility", repro_ok)
    lines.append(line)
    all_ok &= ok

    lines.append("")
    lines.append("FINAL STATUS: PASS" if all_ok else "FINAL STATUS: FAIL")
    print("\n".join(lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
