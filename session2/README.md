# SamaBPE

One **faithful** Hugging Face BPE tokenizer. Four Wikipedia India pages. 10,000-token vocabulary.

**Production:** https://sama-bpe-tokenizer-413.netlify.app

---

## Architecture

- **NFKC** normalization (no punctuation stripping)
- **Metaspace** pretokenizer + decoder (`▁` word boundary)
- **Faithful round-trip gate:** `decode(encode(text))` preserves visible characters
- **SamaBPE:** adaptive multilingual training-weight search (2,570 measured candidates)

---

## Final winner

| Language | Faithful units | Tokens | Fertility | ≤1.2 |
| -------- | -------------: | -----: | --------: | ---- |
| English  | 147,908 | 126,158 | 0.8530 | ✓ |
| Hindi    | 67,473 | 55,978 | 0.8296 | ✓ |
| Telugu   | 27,225 | 22,993 | 0.8446 | ✓ |
| Bengali  | 68,468 | 58,100 | 0.8486 | ✓ |

| Metric | Value |
| ------ | ----- |
| Spread | 0.0233 |
| **Adjusted evaluator score** | **42,893.47** |
| Winning weights | EN 3 · HI 5 · TE 9 · BN 5 |
| Round-trip | PASS (reviewer + 4 corpora) |
| Tokenizer SHA-256 | `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469` |

---

## Reproduce

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

```bash
python encoder.py "India's population is 1,428,627,663."
```

---

## Code map

| File | Role |
| ---- | ---- |
| `python/samabpe/evaluator_contract.py` | Faithful scoring contract |
| `python/samabpe/hf_bpe_trainer.py` | NFKC + Metaspace HF BPE trainer |
| `scripts/run_faithful_weight_search.py` | Weight search with round-trip gate |
| `submission/tokenizer.json` | Frozen HF BPE winner |
| `submission/encoder.py` | Executable encoder |
| `results/resubmission/experiments.json` | 2,570 measured experiments |

## License

MIT
