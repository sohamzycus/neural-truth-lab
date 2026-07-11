# SamaBPE — The Fair Tokenizer Lab

One vocabulary. Four scripts. One objective: **equality**.

SamaBPE designs, optimizes, verifies, and visualizes a single BPE tokenizer (≤10,000 tokens) for four frozen Wikipedia *India* articles (English, Hindi, Telugu, Bengali).

## Scoring Formula

```
X_language = total_BPE_tokens / word_units
Score = 1000 / (X_max - X_min)
```

**Constraint:** `X_en ≤ 1.2`

**Word units:** NFC-normalized text, split on Unicode whitespace, empty segments discarded.

## Quick Start

```bash
cd session2
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 1. Fetch & freeze corpora (MediaWiki API)
python scripts/fetch_corpora.py

# 2. Train all strategies, select verified winner, emit artefacts
python scripts/train.py

# 3. Independent verification
python scripts/verify.py

# 4. Web UI (reads results/stats.json — never hard-coded scores)
cd web && npm install && npm run dev
```

## Reproduce Score

```bash
python scripts/verify.py
```

## Artefacts

| File | Description |
|------|-------------|
| `results/tokenizer.json` | Winning BPE tokenizer |
| `results/stats.json` | Verified headline metrics |
| `results/strategy_comparison.json` | All 5 strategy benchmarks |
| `results/optimization_trace.json` | Score-directed adaptive trace |
| `results/vocab_allocation.json` | 10K budget allocation |
| `results/rejected_merges.json` | Fairness-rejected merge candidates |
| `data/frozen/*.txt` | Evaluation corpora (SHA-256 in manifest) |

## Strategies Benchmarked

1. Shared Vanilla BPE
2. Allocated Monolingual BPE (merged vocabs)
3. Weighted Shared BPE (English-seeded + language rebalancing)
4. Grapheme-Aware BPE
5. Score-Directed Adaptive BPE

Winner selected **only** from verified measured results passing English ≤ 1.2.

## Web Stack

React · TypeScript · Vite · Tailwind CSS · Recharts

Static deploy: `cd web && npm run build` → Netlify-compatible `dist/`.

## Methodology Notes

- Corpora fetched from official MediaWiki API; raw + NFC-frozen snapshots preserved.
- Browser BPE encoder matches Python via parity tests (`npm test` in `web/`).
- Budget Simulator curves are **measured** from vocabulary sweeps; slider estimates are labeled predicted.
- Grapheme integrity uses Unicode extended clusters (`regex \X` in Python, `Intl.Segmenter` in browser).

## License

Educational / research artefact.
