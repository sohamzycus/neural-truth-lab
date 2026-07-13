#!/usr/bin/env python3
"""Train reference-compatible Hugging Face BPE baseline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.hf_bpe_trainer import DEFAULT_WEIGHTS, load_faithful_corpora, train_hf_bpe

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "resubmission" / "baseline"
CORPUS = ROOT / "data" / "faithful"


def main() -> int:
    if not (CORPUS / "en.faithful.md").exists():
        print("Run scripts/build_wiki_faithful_markdown.py first")
        return 1
    corpora = load_faithful_corpora(CORPUS)
    tok_path = OUT / "tokenizer.json"
    tok, meta = train_hf_bpe(corpora, weights=DEFAULT_WEIGHTS, output_path=tok_path)
    metrics_path = OUT / "metrics.json"
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "evaluate_hf_tokenizer.py"),
            "--tokenizer",
            str(tok_path),
            "--corpus-dir",
            str(CORPUS),
            "--output",
            str(metrics_path),
        ]
    )
    record = {
        "strategy": "reference-compatible-baseline",
        "weights": DEFAULT_WEIGHTS,
        **meta,
        "metrics_path": str(metrics_path.relative_to(ROOT)),
    }
    (OUT / "provenance.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    m = json.loads(metrics_path.read_text(encoding="utf-8"))
    print(f"Baseline final_grade={m['scoring']['final_grade']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
