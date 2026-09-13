#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.experiments.lr_sweep import run


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["smoke", "full"], default="full")
    args = p.parse_args()
    run(args.mode)
    print(f"[PASS] learning-rate sweep ({args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
