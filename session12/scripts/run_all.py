#!/usr/bin/env python3
"""Run tests, experiments, plots, and refresh notebook."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    subprocess.check_call([sys.executable, "-m", "pytest", "tests", "-q"], cwd=ROOT)

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from src.experiments import run_all_experiments, save_records, scaling_sweep
    from src.visualization import generate_all_plots

    records = run_all_experiments()
    scaling = scaling_sweep()
    out = ROOT / "outputs" / "experiment_matrix.json"
    save_records(records + scaling, out)
    generate_all_plots(records + scaling, ROOT / "outputs" / "figures")

    subprocess.check_call([sys.executable, "scripts/build_notebook.py"], cwd=ROOT)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
