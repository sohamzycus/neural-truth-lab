#!/usr/bin/env python3
"""One-command demo: tests + experiments."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv" / "bin" / "python"


def main() -> int:
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    steps = [
        [py, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [py, "experiments/run_all.py"],
        [py, "scripts/research_check.py"],
    ]
    for cmd in steps:
        print(">", " ".join(cmd))
        rc = subprocess.call(cmd, cwd=ROOT)
        if rc != 0:
            return rc
    print("\nResults: results/summary.json")
    print("Webapp:  python -m http.server 8765 --directory app  (open http://localhost:8765)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
