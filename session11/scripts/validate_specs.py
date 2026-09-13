#!/usr/bin/env python3
"""Validate all specification files before experiments."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.config_loader import validate_all_specs


def main() -> int:
    errors = validate_all_specs()
    if errors:
        print("[FAIL] specification validation")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[PASS] specification validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
