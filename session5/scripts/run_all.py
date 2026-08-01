#!/usr/bin/env python3
"""Run full Session 5 validation + proxy experiments + cleaning manifest."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent


def run(name: str, script: str) -> bool:
    print(f"\n=== {name} ===")
    r = subprocess.run([sys.executable, str(SCRIPTS / script)], cwd=ROOT)
    ok = r.returncode == 0
    print(f"{'PASS' if ok else 'FAIL'}: {name}")
    return ok


def main() -> int:
    steps = [
        ("Mixture spec validation", "validate_mixture.py"),
        ("Cleaning manifest", "build_cleaning_manifest.py"),
        ("Proxy-1B experiment", "run_proxy_1b.py"),
        ("Proxy-3B experiment", "run_proxy_3b.py"),
    ]
    results = [run(n, s) for n, s in steps]
    passed = sum(results)
    print(f"\n=== Summary: {passed}/{len(steps)} passed ===")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
