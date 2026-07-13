#!/usr/bin/env python3
"""Assemble zero-ambiguity resubmission package after winner is frozen."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "submission"
CORPUS = ROOT / "corpus"
RESULTS = ROOT / "results"


def main() -> int:
    winner_path = RESULTS / "evaluator_winner.json"
    if not winner_path.exists():
        print("Run scripts/train_evaluator_tokenizer.py first")
        return 1

    winner = json.loads(winner_path.read_text(encoding="utf-8"))
    tok_src = ROOT / winner["winner"]["tokenizer_path"]
    hf_src = RESULTS / "tokenizer_hf.json"
    src = hf_src if hf_src.exists() else tok_src

    SUB.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, SUB / "tokenizer.json")
    shutil.copy2(ROOT / "scripts" / "build_wiki_faithful_markdown.py", SUB / "build_wiki_faithful_markdown.py")

    dest_corpus = SUB / "corpus"
    dest_corpus.mkdir(exist_ok=True)
    for lang in ("en", "hi", "te", "bn"):
        for ext in (".faithful.md", ".faithful.txt", ".meta.json"):
            p = CORPUS / f"{lang}{ext}"
            if p.exists():
                shutil.copy2(p, dest_corpus / p.name)

    # Run fresh evaluation into submission/metrics.json
    import subprocess

    subprocess.check_call([sys.executable, str(SUB / "evaluate_tokenizer.py")], cwd=SUB)

    readme = SUB / "README.md"
    m = json.loads((SUB / "metrics.json").read_text(encoding="utf-8"))
    readme.write_text(
        f"""# SamaBPE Resubmission Package

Executable Hugging Face BPE tokenizer evaluated on wiki-faithful Wikipedia India Markdown corpora.

## Reproduce

```bash
pip install -r requirements.txt
python evaluate_tokenizer.py
```

## Encode sample text

```bash
python encoder.py "भारत India"
```

## Verified result (reference — verifier recomputes fresh)

| Metric | Value |
| ------ | ----- |
| Vocabulary | {m['vocabulary_size']} |
| Spread | {m['spread']} |
| Raw score | {m['raw_score']} |
| Hindi penalty | {m['hindi_penalty']} |
| **Adjusted score** | **{m['adjusted_score']}** |
| Tokenizer SHA-256 | `{m['tokenizer_sha256']}` |

Strategy: {winner['winner']['strategy']} · weights `{winner['winner']['weights']}`

## Corpus

Wiki-faithful Markdown snapshots in `corpus/*.faithful.md` (from Wikipedia REST HTML via html2text).

## Scoring

- `fertility(lang) = encoded_tokens / wordish_units`
- Word-ish units: NFKC → replace non-letter/mark/number runs with space → whitespace split
- `raw_score = 1000 / (X_max - X_min)`
- `hindi_penalty = exp(max(0, X_hi/1.2 - 1))`
- `adjusted_score = raw_score / hindi_penalty`
""",
        encoding="utf-8",
    )
    print(f"Submission package → {SUB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
