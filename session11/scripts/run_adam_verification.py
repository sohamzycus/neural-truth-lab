#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.experiments.adam_verification import run


def main() -> int:
    run("full")
    print("[PASS] manual Adam verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
