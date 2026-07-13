# SamaBPE Submission Package

Standard Hugging Face `tokenizer.json` — NFKC + Metaspace BPE, four-language winner.

## Reproduce

```bash
pip install -r requirements.txt
python evaluate_tokenizer.py
```

```bash
python encoder.py "India भारत తెలుగు বাংলা"
```

## Winner (EN & HI < 1.2)

| Language | Eval units | Tokens | Fertility | < 1.2 |
| -------- | ---------: | -----: | --------: | ----- |
| English  | 147,908 | 126,193 | 0.8532 | PASS |
| Hindi    | 67,473 | 55,985 | 0.8297 | PASS |
| Telugu   | 27,225 | 22,997 | 0.8447 | — |
| Bengali  | 68,468 | 58,108 | 0.8487 | — |

| Metric | Value |
| ------ | ----: |
| Spread | 0.0234 |
| Calculated self-score | 42,650.36 |
| Weights | EN 3 · HI 5 · TE 9 · BN 5 |

Tokenizer SHA-256: `9f80405daa8f9a6b1832462bf970d9ff390b7f12c19eaa370ca80002d0fc00b5`

Hardened retrain at winner weights (byte fallback + visible-punctuation initial alphabet) preserves `@`, `€`, `«`, `»` that were absent from Wikipedia snapshots.

Metrics above match `evaluate_tokenizer.py` output from frozen artifacts in this folder.

## Contents

- `tokenizer.json` — shared 10K vocabulary
- `corpus/` — frozen Wikipedia snapshots (`.faithful.txt`, `.faithful.md`, `.meta.json`)
- `encoder.py` — CLI encode/decode
- `evaluate_tokenizer.py` — standalone evaluator
- `evaluator_contract.py` — evaluation units and scoring
- `metrics.json`, `provenance.json`
