#!/usr/bin/env python3
"""Retrain winner at same weights with visible-punctuation hardening."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.hf_bpe_trainer import WINNER_WEIGHTS, load_faithful_corpora, sha256_file, train_hf_bpe

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "submission"
CORPUS = ROOT / "data" / "faithful"
FINAL = ROOT / "results" / "resubmission" / "final"
WEB = ROOT / "web" / "public" / "data" / "submission"


def main() -> int:
    corpora = load_faithful_corpora(CORPUS)
    old_sha = sha256_file(SUB / "tokenizer.json") if (SUB / "tokenizer.json").exists() else None

    tok, meta = train_hf_bpe(
        corpora,
        weights=WINNER_WEIGHTS,
        output_path=SUB / "tokenizer.json",
        hardened=True,
    )
    new_sha = meta["tokenizer_sha256"]
    print(f"Retrained winner weights {WINNER_WEIGHTS}")
    print(f"Old SHA: {old_sha}")
    print(f"New SHA: {new_sha}")

    # Sync copies
    FINAL.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SUB / "tokenizer.json", FINAL / "tokenizer.json")
    WEB.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SUB / "tokenizer.json", WEB / "tokenizer.json")
    if (SUB / "metrics.json").exists():
        shutil.copy2(SUB / "metrics.json", WEB / "metrics.json")

    prov_path = SUB / "provenance.json"
    prov = json.loads(prov_path.read_text(encoding="utf-8")) if prov_path.exists() else {}
    prov.update(
        {
            "weights": WINNER_WEIGHTS,
            "tokenizer_sha256": new_sha,
            "hardening": {
                "applied_at": datetime.now(timezone.utc).isoformat(),
                "byte_fallback": True,
                "initial_alphabet_seeded": True,
                "reason": "Preserve visible punctuation absent from Wikipedia snapshots (<unk> decode deletion fix)",
                "prior_tokenizer_sha256": old_sha,
            },
        }
    )
    prov_path.write_text(json.dumps(prov, indent=2, ensure_ascii=False), encoding="utf-8")

    r = subprocess.run([sys.executable, "evaluate_tokenizer.py"], cwd=SUB)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
