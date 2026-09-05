#!/usr/bin/env python3
"""Run tests, experiments, notebook, README, and audit."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def main() -> None:
    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "scripts/run_experiments.py"])
    run([sys.executable, "build_notebook.py"])
    run([
        "jupyter", "nbconvert", "--to", "notebook", "--execute",
        "Session_10_Truth_Lab.ipynb", "--output", "Session_10_Truth_Lab.ipynb",
    ])
    run([sys.executable, "scripts/generate_readme.py"])
    run([sys.executable, "scripts/audit_submission.py"])
    print("All done.")


if __name__ == "__main__":
    main()
