# Final Submission Audit

Generated: 2026-07-13T18:21:43.822517+00:00

## Verdict: **SUBMISSION READY**

## Tokenizer

| Item | Value | Status |
| ---- | ----- | ------ |
| Path | `submission/tokenizer.json` | VERIFIED |
| Type | Hugging Face BPE | VERIFIED |
| Vocab size | 10000 | VERIFIED |
| Normalizer | NFKC | VERIFIED |
| Pretokenizer | Metaspace | VERIFIED |
| Decoder | Metaspace | VERIFIED |
| SHA-256 | `c7ac20a2af2fddeebc05ce75ce8cc62db2ee2552221f8da7b59d0f86739828d0` | VERIFIED |

## Languages

EN, HI, TE, BN only — VERIFIED (en, hi, te, bn)

## Corpora

- **EN** `submission/corpus/en.faithful.txt` · SHA `beefe609575008bcda18af72589f35bbe6322afb63a54c106ae0dc8190f3a463` · 147,908 eval units — VERIFIED
- **HI** `submission/corpus/hi.faithful.txt` · SHA `e7faf48f3010e942a00927e7d7ab1d15a9bba2946289626a20aec40816c6c5c6` · 67,473 eval units — VERIFIED
- **TE** `submission/corpus/te.faithful.txt` · SHA `d0f5727be7ea9167f300d90ce09101786345289eb6a5b55f3f1d027f09a98c39` · 27,225 eval units — VERIFIED
- **BN** `submission/corpus/bn.faithful.txt` · SHA `be103ace9d5d2ada8e141737f4270ec3e034e27c20c7b190ca218ff4c2129815` · 68,468 eval units — VERIFIED

## Metrics (fresh)

| Lang | Fertility | EN/HI threshold |
| ---- | --------: | --------------- |
| EN | 0.855735 | PASS |
| HI | 0.830228 | PASS |
| TE | 0.850615 | — |
| BN | 0.849083 | — |

Spread: 0.025506 · Raw score: 39206.06 · Hindi penalty: 1.0000 · Adjusted self-score: 39206.06

## Round-trip

- Reviewer sample: PASS
- EN full corpus: PASS
- HI full corpus: PASS
- TE full corpus: PASS
- BN full corpus: PASS

## Experiment integrity

- Total records: 2570 — VERIFIED
- HF BPE runs: 2570
- Unique weight configs: 2570
- NFKC+Metaspace: 2570
- Round-trip passes: 2570
- Both thresholds: 2570
- UI headline: 2,570 real Hugging Face BPE candidates trained and measured

## Artifact parity

- All tokenizer artifacts identical: PASS
- Winner registry SHA match: False

## Playground parity

- Cases: 28 · Pass: 28 · All pass: True

## Clean-room reproduction

- PASS
