# SamaBPE Resubmission Package

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
| Vocabulary | 10000 |
| Spread | 0.08882810507148253 |
| Raw score | 11257.698216068791 |
| Hindi penalty | 2.0905394067626437 |
| **Adjusted score** | **5385.068647666478** |
| Tokenizer SHA-256 | `31fdf2b855ebd8b2d4c5ae4cf6e7780cec1880b1b539c3f3d5c61dbcab0feeff` |

Strategy: boundary_aware_search · weights `{'en': 2, 'hi': 2, 'te': 6, 'bn': 3}`

## Corpus

Wiki-faithful Markdown snapshots in `corpus/*.faithful.md` (from Wikipedia REST HTML via html2text).

## Scoring

- `fertility(lang) = encoded_tokens / wordish_units`
- Word-ish units: NFKC → replace non-letter/mark/number runs with space → whitespace split
- `raw_score = 1000 / (X_max - X_min)`
- `hindi_penalty = exp(max(0, X_hi/1.2 - 1))`
- `adjusted_score = raw_score / hindi_penalty`
