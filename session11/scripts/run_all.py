#!/usr/bin/env python3
"""End-to-end pipeline: validate → experiments → ledger → README → run report → tests."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.experiments import adam_verification, bias_correction, layer_ratios, lr_sweep, schedule_comparison
from src.reporting.ledger import EvidenceLedger


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    p.add_argument("--skip-tests", action="store_true")
    args = p.parse_args()

    print("=== STAGE 1: validate specs ===")
    subprocess.check_call([sys.executable, "scripts/validate_specs.py"], cwd=ROOT)

    print(f"=== STAGE 2: run experiments ({args.mode}) ===")
    ledger_path = ROOT / "outputs" / "evidence_ledger.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = EvidenceLedger(ledger_path)

    adam_verification.run(args.mode, ledger)
    bias_correction.run(args.mode, ledger)
    layer_ratios.run(args.mode, ledger)
    schedule_comparison.run(args.mode, ledger)
    lr_sweep.run(args.mode, ledger)
    ledger.write_markdown()

    print("=== STAGE 3: generate README from artifacts ===")
    subprocess.check_call([sys.executable, "scripts/generate_readme.py"], cwd=ROOT)

    print("=== STAGE 4: generate graphical run report ===")
    subprocess.check_call([sys.executable, "scripts/generate_run_report.py", "--mode", args.mode], cwd=ROOT)

    if not args.skip_tests:
        print("=== STAGE 5: pytest ===")
        subprocess.check_call([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT)

    print(f"Pipeline complete ({args.mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
