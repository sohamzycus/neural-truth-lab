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
| English  | 147,908 | 126,158 | 0.8530 | PASS |
| Hindi    | 67,473 | 55,978 | 0.8296 | PASS |
| Telugu   | 27,225 | 22,993 | 0.8446 | — |
| Bengali  | 68,468 | 58,100 | 0.8486 | — |

| Metric | Value |
| ------ | ----: |
| Spread | 0.0233 |
| Calculated self-score | 42,893.47 |
| Weights | EN 3 · HI 5 · TE 9 · BN 5 |

Tokenizer SHA-256: `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469`

Metrics above match `evaluate_tokenizer.py` output from frozen artifacts in this folder.

## Contents

- `tokenizer.json` — shared 10K vocabulary
- `corpus/` — frozen Wikipedia snapshots (`.faithful.txt`, `.faithful.md`, `.meta.json`)
- `encoder.py` — CLI encode/decode
- `evaluate_tokenizer.py` — standalone evaluator
- `evaluator_contract.py` — evaluation units and scoring
- `metrics.json`, `provenance.json`
