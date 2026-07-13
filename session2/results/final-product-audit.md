# SamaBPE Final Product Audit

Generated from live artifacts in `session2/`.

## Executive verdict: **SUBMISSION READY**

---

## Tokenizer

| Claim | Value | Status |
| ----- | ----- | ------ |
| Path | `submission/tokenizer.json` | VERIFIED |
| Format | Hugging Face `tokenizers` JSON (BPE) | VERIFIED |
| Vocabulary size | 10000 | VERIFIED |
| SHA-256 | `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469` | VERIFIED |
| Normalizer | NFKC | VERIFIED |
| Pretokenizer | Metaspace | VERIFIED |
| Decoder | Metaspace | VERIFIED |

## Corpora (frozen Wikipedia snapshots)

| Lang | Path | SHA-256 | Eval units | Revision | Status |
| ---- | ---- | ------- | ---------: | -------- | ------ |
| EN | `submission/corpus/en.faithful.txt` | `beefe609575008bc…` | 147,908 | 1363833574 | VERIFIED |
| HI | `submission/corpus/hi.faithful.txt` | `e7faf48f3010e942…` | 67,473 | 6579409 | VERIFIED |
| TE | `submission/corpus/te.faithful.txt` | `d0f5727be7ea9167…` | 27,225 | 4848340 | VERIFIED |
| BN | `submission/corpus/bn.faithful.txt` | `be103ace9d5d2ada…` | 68,468 | 9043433 | VERIFIED |

## Baseline vs winner weights

| | EN | HI | TE | BN | Status |
| - | -: | -: | -: | -: | ------ |
| Baseline | 3 | 4 | 4 | 2 | VERIFIED |
| Winner | 3 | 5 | 9 | 5 | VERIFIED |

## Metrics (fresh evaluation)

| Metric | Value | vs metrics.json |
| tokenizer.sha256 | 8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469 | VERIFIED |
| en.faithful_units | 147908 | VERIFIED |
| en.tokens | 126158 | VERIFIED |
| en.fertility | 0.8529491305406063 | VERIFIED |
| hi.faithful_units | 67473 | VERIFIED |
| hi.tokens | 55978 | VERIFIED |
| hi.fertility | 0.8296355579268745 | VERIFIED |
| te.faithful_units | 27225 | VERIFIED |
| te.tokens | 22993 | VERIFIED |
| te.fertility | 0.84455463728191 | VERIFIED |
| bn.faithful_units | 68468 | VERIFIED |
| bn.tokens | 58100 | VERIFIED |
| bn.fertility | 0.8485715954898638 | VERIFIED |
| spread | 0.023313572613731792 | VERIFIED |
| raw_score | 42893.46882043277 | VERIFIED |
| hindi_penalty | 1.0 | VERIFIED |
| adjusted_score | 42893.46882043277 | VERIFIED |

## Experiment integrity (2,570 claim)

| Check | Value | Status |
| ----- | ----- | ------ |
| Registry architecture | NFKC+Metaspace | VERIFIED |
| Experiments in registry | 2570 | VERIFIED |
| Header total_measured | 2570 | VERIFIED |
| Unique weight configs | 2570 | VERIFIED |
| Tokenizer engine | {'huggingface-bpe': 2570} | VERIFIED |
| Normalizers | {'NFKC': 2570} | VERIFIED |
| Pretokenizers | {'Metaspace': 2570} | VERIFIED |
| Status breakdown | {'VALID_MEASURED': 2570} | VERIFIED |
| Passed lossless round-trip | 2570 | VERIFIED |
| Passed EN < 1.2 | 2570 | VERIFIED |
| Passed HI < 1.2 | 2570 | VERIFIED |
| Passed both thresholds | 2570 | VERIFIED |
| Winner experiment ID | `faithful-hf-2361` | VERIFIED |

**Conclusion:** All 2,570 registry entries are real Hugging Face BPE training runs under NFKC+Metaspace on the same four frozen corpora, with unique weight configurations. Legacy non-current experiments are not mixed into this registry.

## Experiment funnel (UI)

- Candidates trained: 2570
- Passed round-trip: 2570
- Passed both EN & HI < 1.2: 2570
- Winner: 1

## Vocabulary composition (winner)

- latin_dominant: 4113
- devanagari_dominant: 1684
- telugu_dominant: 1478
- bengali_dominant: 1703
- shared_punctuation_digits_symbols: 895
- mixed_script: 113
- other_unicode: 13
- special_token: 1
- **Sum:** 10000 (vocab 10000) — VERIFIED

## Baseline → winner vocabulary shift

- latin_dominant: baseline 4779 → winner 4113 (Δ -666)
- devanagari_dominant: baseline 1963 → winner 1684 (Δ -279)
- telugu_dominant: baseline 1032 → winner 1478 (Δ +446)
- bengali_dominant: baseline 1153 → winner 1703 (Δ +550)
- shared_punctuation_digits_symbols: baseline 958 → winner 895 (Δ -63)
- mixed_script: baseline 101 → winner 113 (Δ +12)
- other_unicode: baseline 13 → winner 13 (Δ +0)
- special_token: baseline 1 → winner 1 (Δ +0)

## Vocabulary utilization

- EN unique token IDs: 4,331
- HI unique token IDs: 4,124
- TE unique token IDs: 3,220
- BN unique token IDs: 4,531
- Used by ≥1 corpus: 9,211
- Unused by all four: 789
- Used by exactly one: 5,619
- Used by all four: 1,092

## Reproduction commands

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

```bash
python scripts/generate_verified_submission_data.py
```

## Playground tokenizer

- Browser loads `web/public/data/submission/tokenizer.json` (same SHA as submission)
- Encoder: `web/src/lib/hf-encoder.ts` (NFKC + Metaspace + BPE)
- Parity fixtures: `web/public/data/playground_parity.json`

## Claim classification summary

- All metrics.json claims: VERIFIED

## Risks (non-blocking)

- Rare Unicode symbols (€, @) fail isolated round-trip stress sample
