# SamaBPE Resubmission Package

Standard Hugging Face `tokenizer.json` evaluated on wiki-faithful Wikipedia India Markdown corpora.

## Reproduce

```bash
pip install -r requirements.txt
python evaluate_tokenizer.py
```

## Encode sample text

```bash
python encoder.py "भारत India বাংলা తెలుగు"
```

## Verified result (evaluator recomputes fresh)

| Language | Word-ish | Tokens | Fertility |
| -------- | -------: | -----: | --------: |
| English  | 69411 | 99168 | 1.428707 |
| Hindi    | 31941 | 44257 | 1.385586 |
| Telugu   | 11817 | 16620 | 1.406448 |
| Bengali  | 30806 | 43045 | 1.397293 |

| Metric | Value |
| ------ | ----- |
| Spread | 0.043121 |
| Raw score | 23190.37 |
| Hindi penalty | 1.1673× |
| **Final grade** | **19867.44** |
| Vocabulary | 10,000 |
| Tokenizer SHA-256 | `cc5f9dc496391d289e9a3c5cdc22dc2b80f23d08aacd8126bdf83b89ea6b733a` |

Strategy: adaptive-weight-search · weights EN 2 · HI 3 · TE 6 · BN 4

## Corpus

Faithful Markdown in `corpus/*.faithful.md` (Wikipedia REST HTML → markdownify pipeline).

## Scoring

Implemented in `evaluator_contract.py` — word-ish denominator, raw score, Hindi penalty, final grade.
