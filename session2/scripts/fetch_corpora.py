#!/usr/bin/env python3
"""Fetch Wikipedia India corpora."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import fetch_all

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    manifest = fetch_all(DATA)
    for lang, rec in manifest.items():
        print(f"{lang}: {rec.word_unit_count} word units, sha256={rec.sha256_frozen[:16]}...")


if __name__ == "__main__":
    main()
