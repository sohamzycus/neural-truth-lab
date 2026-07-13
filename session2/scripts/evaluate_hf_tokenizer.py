#!/usr/bin/env python3
"""Canonical faithful Hugging Face tokenizer evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from tokenizers import Tokenizer

from samabpe.evaluator_contract import LANGS, REVIEWER_SAMPLE, faithful_units, verify_roundtrip
from samabpe.hf_bpe_trainer import evaluate_tokenizer, sha256_file, verify_tokenizer_roundtrip

ROOT = Path(__file__).resolve().parents[1]


def evaluate(tokenizer_path: Path, corpus_dir: Path) -> dict:
    tok = Tokenizer.from_file(str(tokenizer_path))
    corpora = {}
    corpus_sha = {}
    for lang in LANGS:
        for ext in (".faithful.txt", ".faithful.md"):
            p = corpus_dir / f"{lang}{ext}"
            if p.exists():
                text = p.read_text(encoding="utf-8")
                break
        else:
            raise FileNotFoundError(f"missing corpus for {lang}")
        corpora[lang] = text
        corpus_sha[lang] = hashlib.sha256(text.encode("utf-8")).hexdigest()

    roundtrip = verify_tokenizer_roundtrip(tok, corpora)
    reviewer_enc = tok.encode(REVIEWER_SAMPLE)
    reviewer_dec = tok.decode(reviewer_enc.ids)

    metrics = evaluate_tokenizer(tok, corpora)
    vocab_size = tok.get_vocab_size(with_added_tokens=True)

    languages = {}
    for lang in LANGS:
        fu = faithful_units(corpora[lang])
        tc = metrics["token_counts"][lang]
        languages[lang] = {
            "faithful_units": fu,
            "wordish_units": fu,
            "tokens": tc,
            "fertility": metrics["fertilities"][lang],
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tokenizer": {
            "format": "huggingface-tokenizers",
            "engine": "BPE",
            "normalizer": "NFKC",
            "pretokenizer": "Metaspace",
            "decoder": "Metaspace",
            "path": str(tokenizer_path),
            "vocab_size": vocab_size,
            "sha256": sha256_file(tokenizer_path),
            "vocab_constraint_pass": vocab_size <= 10_000,
        },
        "corpus_dir": str(corpus_dir),
        "corpus_sha256": corpus_sha,
        "roundtrip": {
            "reviewer_sample": roundtrip["reviewer_sample"],
            "reviewer_tokens": reviewer_enc.tokens,
            "reviewer_decoded": reviewer_dec,
            "full_corpus": roundtrip["full_corpus"],
            "valid": roundtrip["valid"],
        },
        "languages": languages,
        "thresholds": metrics["thresholds"],
        "scoring": {
            "x_min": metrics["x_min"],
            "x_max": metrics["x_max"],
            "spread": metrics["spread"],
            "raw_score": metrics["raw_score"],
            "hindi_penalty": metrics["hindi_penalty"],
            "final_grade": metrics["final_grade"],
            "adjusted_score": metrics["adjusted_score"],
        },
        "token_counts": metrics["token_counts"],
        "faithful_unit_counts": metrics["faithful_unit_counts"],
        "fertilities": metrics["fertilities"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tokenizer", type=Path, required=True)
    p.add_argument("--corpus-dir", type=Path, default=ROOT / "data" / "faithful")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = evaluate(args.tokenizer, args.corpus_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"  roundtrip={result['roundtrip']['valid']} adjusted={result['scoring']['adjusted_score']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
