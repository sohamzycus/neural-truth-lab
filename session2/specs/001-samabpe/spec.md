# SamaBPE — The Fair Tokenizer Lab

**Status:** Approved for implementation  
**Constitution:** v1.0.0

## Objective

Design, optimize, verify, visualize, and export one BPE tokenizer (≤10,000 tokens) for four frozen Wikipedia "India" articles (en, hi, te, bn) maximizing:

```
Score = 1000 / (X_max - X_min)
where X_lang = BPE_tokens / word_units
```

Constraint: `X_en ≤ 1.2`

## Word-Unit Denominator (Official)

1. Apply Unicode NFC normalization to the full frozen article text.
2. Split on Unicode whitespace (`\s` with UNICODE flag).
3. Discard empty segments.
4. Count remaining segments — each is one **word unit**.

Rationale: evaluator-compatible whitespace tokenization on normalized text; documented and deterministic.

## Pretokenization Modes

| Mode | Description |
|------|-------------|
| `whitespace` | Split on whitespace; BPE operates on space-delimited words |
| `character` | UTF-8 code points as initial symbols |
| `grapheme` | Extended grapheme clusters via `\X` as initial symbols |

## Five Strategies

1. **shared_vanilla** — pooled corpus, single BPE
2. **allocated_monolingual** — per-language BPE, merged vocab + merges
3. **weighted_shared** — shared BPE with language-weighted pair frequencies
4. **grapheme_aware** — grapheme pretokenization + shared BPE
5. **score_directed_adaptive** — greedy merge selection minimizing max-min fertility gap

## Artefacts

`tokenizer.json`, `vocab.json`, `vocab.txt`, `merges.txt`, frozen/raw corpora, `stats.json`, `optimization_trace.json`, `vocab_allocation.json`, `grapheme_stats.json`, `rejected_merges.json`, SHA-256 manifest.

## UI Stack

React, TypeScript, Vite, Tailwind, Recharts. Static deploy on Netlify. Reads `public/data/results/stats.json`.

## Acceptance

- [ ] `python scripts/verify.py` passes all assertions
- [ ] Five strategies benchmarked in `strategy_comparison.json`
- [ ] Winner matches verified highest score
- [ ] Browser encoder parity tests pass
- [ ] `npm run build` succeeds
