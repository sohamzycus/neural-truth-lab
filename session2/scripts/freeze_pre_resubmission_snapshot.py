#!/usr/bin/env python3
"""Phase 1 — freeze current submission state before resubmission work."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import WIKI_CONFIG, sha256_text
from samabpe.scoring import compute_score
from samabpe.verify_core import run_verification, sha256_file
from samabpe.word_units import count_word_units, normalize_nfc

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA_FROZEN = ROOT / "data" / "frozen"
OUT = RESULTS / "pre_resubmission_snapshot.json"


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def main() -> int:
    tok_path = RESULTS / "tokenizer.json"
    if not tok_path.exists():
        print("ERROR: results/tokenizer.json missing")
        return 1

    result = run_verification(tok_path, DATA_FROZEN, winning_strategy="weighted-shared-bpe")
    stats_path = RESULTS / "stats.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}

    corpus_hashes = {}
    for lang in WIKI_CONFIG:
        p = DATA_FROZEN / f"{lang}_india.txt"
        corpus_hashes[lang] = sha256_text(p.read_text(encoding="utf-8")) if p.exists() else None

    snapshot = {
        "label": "pre_resubmission_freeze",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "tokenizer": {
            "path": str(tok_path.relative_to(ROOT)),
            "sha256": sha256_file(tok_path),
            "format": "samabpe-custom-v1.0",
            "vocabulary_size": result.vocabulary_size,
            "encoder_paths": [
                "python/samabpe/bpe.py",
                "web/src/lib/bpe.ts",
            ],
        },
        "displayed_metrics": {
            "source": "results/stats.json",
            "fertilities": stats.get("fertilities", result.fertilities),
            "gap": stats.get("max_min_gap", result.max_min_gap),
            "score": stats.get("score", result.score),
            "languages": stats.get("languages", []),
        },
        "verification_run": {
            "fertilities": result.fertilities,
            "gap": result.max_min_gap,
            "score": result.score,
            "english_pass": result.english_pass,
        },
        "corpus": {
            "paths": {lang: f"data/frozen/{lang}_india.txt" for lang in WIKI_CONFIG},
            "sha256": corpus_hashes,
            "source": "Wikipedia plain-text extract (MediaWiki API explaintext=true)",
            "urls": {
                lang: f"https://{cfg['host']}/wiki/{cfg['title']}"
                for lang, cfg in WIKI_CONFIG.items()
            },
        },
        "evaluation_contract_old": {
            "normalization": "NFC only (freeze_text)",
            "pretokenization": "whitespace split + </w> suffix on words",
            "denominator": "count_word_units: NFC → split on Unicode whitespace → non-empty segments",
            "denominator_module": "python/samabpe/word_units.py::count_word_units",
            "scoring": "score = 1000 / (X_max - X_min); no Hindi penalty",
            "scoring_module": "python/samabpe/scoring.py::compute_score",
            "english_constraint": "X_en <= 1.2 (training constraint, not exponential penalty)",
        },
        "notes": [
            "Custom JSON tokenizer format — not HuggingFace tokenizers loadable.",
            "Do not overwrite results/tokenizer.json during resubmission work.",
        ],
    }

    OUT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"  commit: {snapshot['git_commit']}")
    print(f"  score:  {snapshot['displayed_metrics']['score']}")
    print(f"  sha256: {snapshot['tokenizer']['sha256'][:16]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
