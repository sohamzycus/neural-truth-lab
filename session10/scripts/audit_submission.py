#!/usr/bin/env python3
"""Final submission audit for Session 10 Truth Lab."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "outputs" / "results.json"


def check(name: str, ok: bool, detail: str = "") -> tuple[str, bool]:
    status = "PASS" if ok else "INVESTIGATE"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    return line, ok


def main() -> int:
    lines = ["SESSION 10 FINAL AUDIT", ""]
    all_ok = True

    readme_ok = (ROOT / "README.md").exists()
    nb_ok = (ROOT / "Session_10_Truth_Lab.ipynb").exists()
    src_ok = (ROOT / "truth_lab").is_dir()
    tests_ok = (ROOT / "tests" / "test_truth_lab.py").exists()
    results_ok = RESULTS.exists()
    plots_ok = (ROOT / "outputs" / "plots" / "accumulation_naive_vs_correct.png").exists()
    plots2_ok = (ROOT / "outputs" / "plots" / "loss_and_grad_norm.png").exists()

    for label, ok in [
        ("README exists", readme_ok),
        ("Notebook exists", nb_ok),
        ("Source package exists", src_ok),
        ("Tests exist", tests_ok),
        ("results.json exists", results_ok),
        ("Accumulation plot exists", plots_ok),
        ("Grad/loss plot exists", plots2_ok),
    ]:
        line, ok = check(label, ok)
        lines.append(line)
        all_ok &= ok

    if results_ok:
        r = json.loads(RESULTS.read_text())
        required = ["tensor_trace", "gradient_check", "accumulation", "grad_norm", "mfu", "float_repr"]
        for key in required:
            ok = key in r
            line, ok = check(f"results.{key} present", ok)
            lines.append(line)
            all_ok &= ok

        gc = r.get("gradient_check", {})
        gc_ok = "verdict" in gc and "finite_diff" in gc
        line, ok = check("Gradient check result", gc_ok, gc.get("verdict", ""))
        lines.append(line)
        all_ok &= ok

        acc = r.get("accumulation", {})
        acc_ok = acc.get("max_loss_diff", 0) > 0
        line, ok = check("Accumulation comparison", acc_ok, f"max_diff={acc.get('max_loss_diff', 0):.4f}")
        lines.append(line)
        all_ok &= ok

        mfu = r.get("mfu", {})
        mfu_val = mfu.get("mfu", mfu.get("mfu_percent", -1) / 100 if "mfu_percent" in mfu else -1)
        if "mfu_percent" in mfu and "mfu" not in mfu:
            mfu_val = mfu["mfu_percent"] / 100
        mfu_ok = isinstance(mfu_val, (int, float)) and 0 <= mfu_val <= 1
        line, ok = check("MFU in valid range", mfu_ok, f"mfu={mfu_val}")
        lines.append(line)
        all_ok &= ok

        fp = r.get("float_repr", {})
        fp_ok = bool(fp.get("formats") or fp.get("table_markdown"))
        line, ok = check("Precision results", fp_ok)
        lines.append(line)
        all_ok &= ok

        tr = r.get("truth_report", {})
        for k in ("tensor_shapes", "gradient", "accumulation", "mfu", "precision"):
            if k in tr:
                lines.append(f"  truth_report.{k}: {tr[k]}")

    # Run tests
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        tests_pass = proc.returncode == 0
        line, ok = check("Tests", tests_pass, proc.stdout.strip().split("\n")[-1] if proc.stdout else "")
        lines.append(line)
        all_ok &= ok
    except Exception as e:
        line, _ = check("Tests", False, str(e))
        lines.append(line)
        all_ok = False

    lines.append("")
    lines.append("FINAL STATUS: READY FOR REVIEW" if all_ok else "FINAL STATUS: NEEDS INVESTIGATION")
    print("\n".join(lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
