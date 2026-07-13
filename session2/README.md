# SamaBPE

One standard **Hugging Face BPE** tokenizer. Four languages. 10,000-token maximum vocabulary. **Adaptive multilingual weight search** with **threshold-aware winner selection**.

**Production:** https://sama-bpe-tokenizer-413.netlify.app

---

## What did I build?

**SamaBPE** trains real Hugging Face BPE candidates, measures them on wiki-faithful Wikipedia India Markdown corpora, and selects the best measured winner under explicit fertility thresholds.

- **Hugging Face BPE** = tokenizer engine (standard `tokenizer.json`)
- **SamaBPE** = training-time multilingual weight search (weights do not change at runtime)

---

## Final submission winner (threshold-aware)

| Language | Word-ish | Tokens | Fertility | ≤1.2 |
| -------- | -------: | -----: | --------: | ---- |
| English  | 69411 | 99304 | 1.4307 | **> 1.2** |
| Hindi    | 31941 | 38214 | 1.1964 | ✓ |
| Telugu   | 11817 | 18605 | 1.5744 | |
| Bengali  | 30806 | 49037 | 1.5918 | |

| Metric | Value |
| ------ | ----- |
| Spread | 0.3954 |
| Raw score | 2529.04 |
| Hindi penalty | 1.0× |
| **Adjusted evaluator score** | **2529.04** |
| Winning weights | EN 1 · HI 3 · TE 2 · BN 1 |
| Constraint class | **B** (Hindi ≤1.2; English >1.2) |
| Tokenizer SHA-256 | `b0cc0fcd7009ee998f64bc8a653718fc048ff5d813804ca030c2c83236bea331` |

**No Class A candidate** (EN≤1.2 and HI≤1.2) was found among **2,971** measured tokenizers after threshold-aware search. See `results/resubmission/comparison.json`.

---

## Reproduce

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

```bash
python encoder.py "भारत India বাংলা తెలుగు"
```

---

## Experiment comparison

| Candidate | Adjusted score | Status |
| --------- | -------------: | ------ |
| Baseline (3/4/4/2) | 3495.28 | Baseline |
| Best unconstrained (2/3/6/4) | 19,867.44 | High-score experiment (Class C) |
| **Final submission (1/3/2/1)** | **2529.04** | Threshold-aware winner (Class B) |

---

## Code map

| File | Role |
| ---- | ---- |
| `python/samabpe/evaluator_contract.py` | Scoring contract |
| `python/samabpe/weight_optimizer.py` | Constraint classes A/B/C + winner selection |
| `scripts/run_threshold_search.py` | Threshold-aware search |
| `submission/tokenizer.json` | Frozen HF BPE winner |
| `submission/encoder.py` | Executable encoder |
| `results/resubmission/experiments.json` | 2,971 measured experiments |

## License

MIT
