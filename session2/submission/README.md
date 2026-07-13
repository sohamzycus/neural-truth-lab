# SamaBPE Resubmission Package

Standard Hugging Face `tokenizer.json` — threshold-aware winner.

## Reproduce

```bash
pip install -r requirements.txt
python evaluate_tokenizer.py
```

## Winner (Class B — Hindi ≤1.2, English >1.2)

| Language | Fertility | ≤1.2 |
| -------- | --------: | ---- |
| English  | 1.4307 | > 1.2 |
| Hindi    | 1.1964 | ✓ |
| Telugu   | 1.5744 | |
| Bengali  | 1.5918 | |

Adjusted evaluator score: **2529.04** · Weights EN 1 · HI 3 · TE 2 · BN 1

SHA-256: `b0cc0fcd7009ee998f64bc8a653718fc048ff5d813804ca030c2c83236bea331`

No Class A candidate (EN≤1.2 & HI≤1.2) found in 2,971 measured experiments.
