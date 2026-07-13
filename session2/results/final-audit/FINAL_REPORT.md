# SamaBPE Final Pre-Submission Audit Report

Generated from independent recomputation of `submission/tokenizer.json` + `submission/corpus/`.

## A. Executive verdict

**SUBMISSION READY**

The frozen faithful tokenizer loads as standard HF BPE (NFKC + Metaspace), passes the reviewer regression sample and all four full-corpus round-trips, satisfies EN/HI fertility &lt; 1.2, and all reported metrics in `submission/metrics.json` match a fresh evaluator run. One documented risk: an isolated rare-symbol stress string (`€`, `@`) fails NFKC round-trip — not present as a full-corpus failure.

## B. Pre-change discrepancies

| Claim | Where found | Fresh verified value | Severity | Resolution |
| ----- | ----------- | -------------------- | -------- | ---------- |
| UI loaded `resubmission_metrics.json` with absolute machine paths | `web/src/App.tsx` | N/A | STALE | UI now loads `verifiedSubmission.json` |
| Legacy explore lab (BudgetSimulator, vocab attribution) implied per-language allocation | `App.tsx` (old) | N/A | INVALID | Removed from main narrative |
| Prior README Class B / word-ish metrics | `README.md` | Faithful metrics | STALE | README rewritten |
| `427` / `2971` experiment counts mixed architectures | old UI copy | 2,570 faithful only | DISCREPANCY | UI shows faithful registry count only |
| Rare symbol round-trip stress sample | audit samples | FAIL | Risk | Documented in §O |
| `metrics.json` trusted without recomputation | general | All VERIFIED vs fresh | — | Consistency test added |

## C. Exact active languages

**English, Hindi, Telugu, Bengali** (`en`, `hi`, `te`, `bn`).

Maithili: **not in active pipeline**. Grep hits on `main`, `remain` are vocabulary tokens, not language `mai`.

## D. Tokenizer architecture

| Property | Actual |
| -------- | ------ |
| Model | BPE |
| Vocab size | 10,000 |
| Normalizer | NFKC |
| Pretokenizer | Metaspace, replacement `▁`, prepend_scheme `never` |
| Decoder | Metaspace, replacement `▁`, prepend_scheme `never` |
| SHA-256 | `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469` |

## E. Reviewer failure closure

| Field | Value |
| ----- | ----- |
| Input | `India's population is 1,428,627,663.` |
| Faithful units | `India`, `'`, `s`, `population`, `is`, `1`, `,`, `428`, `,`, `627`, `,`, `663`, `.` (13 units) |
| BPE tokens | `India`, `'s`, `▁population`, `▁is`, `▁1,`, `4`, `28`, `,`, `6`, `27`, `,`, `66`, `3.` |
| Decoded | `India's population is 1,428,627,663.` |
| Visible round-trip | **PASS** |

## F. Full corpus faithfulness

| Corpus | Result |
| ------ | ------ |
| EN | PASS |
| HI | PASS |
| TE | PASS |
| BN | PASS |

## G. Freshly reproduced metrics

| Language | Corpus hash (prefix) | Faithful units | Tokens | Fertility | Threshold |
| -------- | -------------------- | -------------: | -----: | --------: | --------- |
| EN | `beefe609…` | 147,908 | 126,158 | 0.852949 | PASS |
| HI | `e7faf48f…` | 67,473 | 55,978 | 0.829636 | PASS |
| TE | `d0f5727b…` | 27,225 | 22,993 | 0.844555 | — |
| BN | `be103ace…` | 68,468 | 58,100 | 0.848572 | — |

| Metric | Value |
| ------ | ----- |
| Spread | 0.023314 |
| Raw score | 42,893.47 |
| Hindi penalty | 1.0× |
| Adjusted score | 42,893.47 |

## H. Why fertility is below 1

Faithful units count punctuation separately (13 units on reviewer sample). BPE merges substrings (`'s`, `▁1,`, `3.`) so **13 BPE tokens / 13 units = 1.0** on the sample; corpus-wide fertilities are **0.83–0.85** because multi-unit merges are common across Wikipedia Markdown.

## I. 10K vocabulary composition

| Category | Tokens | % |
| -------- | -----: | -: |
| Latin-dominant | 4,113 | 41.1% |
| Devanagari-dominant | 1,684 | 16.8% |
| Telugu-dominant | 1,478 | 14.8% |
| Bengali-dominant | 1,703 | 17.0% |
| Shared punctuation/digits/symbols | 895 | 9.0% |
| Mixed-script | 113 | 1.1% |
| Other Unicode | 13 | 0.1% |
| Special tokens | 1 | 0.0% |
| **Total** | **10,000** | **100%** |

`sum == vocab_size`: **verified**

## J. Vocabulary utilization

| Metric | Count |
| ------ | ----: |
| EN unique IDs | 4,331 |
| HI unique IDs | 4,124 |
| TE unique IDs | 3,220 |
| BN unique IDs | 4,531 |
| Used by ≥1 corpus | 9,211 |
| Unused by all four | 789 |
| Used by exactly one | 5,619 |
| Used by exactly two | 1,281 |
| Used by exactly three | 1,219 |
| Used by all four | 1,092 |

## K. SamaBPE experiment integrity

| Item | Value |
| ---- | ----- |
| Baseline weights | EN 3 · HI 4 · TE 4 · BN 2 |
| Winner weights | EN 3 · HI 5 · TE 9 · BN 5 |
| Current faithful experiments | 2,570 |
| Legacy non-faithful | separate prior registry (not used for claims) |
| Valid candidates (round-trip) | 2,570 |
| Both EN & HI &lt; 1.2 | 2,570 |

## L. Cross-source consistency

Fresh evaluator vs `submission/metrics.json` vs `verifiedSubmission.json` vs `provenance.json`: **all VERIFIED** (see `python/tests/test_submission_consistency.py`).

## M. Files changed

- `python/samabpe/submission_audit.py` — audit library
- `scripts/{run_final_audit,explain_fertility,analyze_vocabulary,generate_verified_submission_data}.py`
- `python/tests/test_submission_consistency.py`
- `web/src/components/VerifiedSections.tsx`, `App.tsx`, `types.ts`
- `README.md`, `results/final-audit/*`, `web/public/data/verifiedSubmission.json`

## N. Tests executed

| Command | Result |
| ------- | ------ |
| `python -m pytest python/tests/` | PASS (90) |
| `python scripts/run_final_audit.py` | PASS (SUBMISSION READY) |
| `cd submission && python evaluate_tokenizer.py` | PASS |
| `npm test` (web) | PASS (12) |
| `npm run build:netlify` | PASS |

## O. Remaining risks

1. **Rare Unicode stress sample** (`€`, `@`) fails isolated NFKC round-trip — not a full-corpus failure; document if reviewers test exotic currency keyboards.
2. **789 vocabulary entries** never appear in any of the four evaluation corpora (normal for 10K BPE budget).
3. **Reproducibility** requires the committed `submission/corpus/*.faithful.txt` bytes; Wikipedia revision IDs in meta are for provenance only.
