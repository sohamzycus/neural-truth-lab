"""Playground parity: browser HF encoder must match submission tokenizer exactly."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "web" / "public" / "data" / "playground_parity.json"
HF_TEST = ROOT / "web" / "src" / "lib" / "hf-encoder.test.ts"


def test_fixtures_exist_and_match_python_encoder() -> None:
    assert FIXTURES.exists(), "Run scripts/export_playground_parity.py first"
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(ROOT / "submission" / "tokenizer.json"))
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(data["cases"]) >= 20
    for case in data["cases"]:
        enc = tok.encode(case["text"])
        assert enc.tokens == case["tokens"], case["text"]
        assert enc.ids == case["ids"], case["text"]
        assert len(enc.ids) == case["count"]


def test_vitest_parity_passes() -> None:
    r = subprocess.run(
        ["npm", "test", "--", "hf-encoder.test.ts"],
        cwd=ROOT / "web",
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
