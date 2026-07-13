# SamaBPE

One standard **Hugging Face BPE** tokenizer. Four languages. 10,000-token maximum vocabulary. **Adaptive multilingual weight search** optimized for the actual **final grade** — not raw score alone.

**Production:** https://sama-bpe-tokenizer-413.netlify.app

---

## Final verified result

| Language | Word-ish Units | Encoded Tokens | Fertility |
| -------- | -------------: | -------------: | --------: |
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
| Vocabulary size | 10,000 |
| Tokenizer SHA-256 | `cc5f9dc496391d289e9a3c5cdc22dc2b80f23d08aacd8126bdf83b89ea6b733a` |
| Winning weights | EN 2 · HI 3 · TE 6 · BN 4 |

Download: [`submission/tokenizer.json`](submission/tokenizer.json)

---

## What is innovative?

SamaBPE does **not** replace standard BPE with a custom runtime tokenizer. It uses standard Hugging Face BPE and innovates in **training-time multilingual weight search**. Each candidate is a real tokenizer trained and evaluated against the same faithful corpora. The candidate with the highest **measured final grade** wins.

```
Choose weights → Train HF BPE → Evaluate 4 corpora → Final grade → Next weights → Winner
```

---

## Reproduce

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

## Try the encoder

```bash
python encoder.py "भारत India বাংলা తెలుగు"
```

---

## Evaluator contract

- **Corpus:** wiki-faithful Markdown (`data/faithful/*.faithful.md`) — Wikipedia REST HTML → BeautifulSoup → markdownify
- **Normalizer:** NFKC + replace `[^\p{L}\p{M}\p{N}]+` with space (serialized in `tokenizer.json`)
- **Pretokenizer:** whitespace
- **Denominator:** word-ish units (`[\p{L}\p{M}\p{N}]+` after NFKC)
- **Fertility:** encoded tokens ÷ word-ish units
- **Raw score:** `1000 / (X_max − X_min)`
- **Hindi penalty:** `exp(max(0, X_hi / 1.2 − 1))`
- **Final grade:** `raw_score / hindi_penalty` ← optimization objective

Single source of truth: `python/samabpe/evaluator_contract.py`

---

## Code map

| File | Role |
| ---- | ---- |
| `python/samabpe/evaluator_contract.py` | Normalization, word-ish units, scoring |
| `python/samabpe/hf_bpe_trainer.py` | Standard HF BPE training |
| `python/samabpe/weight_optimizer.py` | Adaptive weight search |
| `scripts/build_wiki_faithful_markdown.py` | Faithful corpus builder |
| `scripts/evaluate_hf_tokenizer.py` | Canonical evaluator CLI |
| `scripts/train_hf_baseline.py` | Reference baseline (weights 3/4/4/2) |
| `scripts/run_weight_search.py` | Coarse + neighbor search → winner |
| `scripts/sync_resubmission_to_web.py` | Sync to `submission/` and web |
| `submission/encoder.py` | Executable encoder |
| `submission/evaluate_tokenizer.py` | Standalone reviewer verifier |
| `results/resubmission/experiments.json` | Measured experiment registry |

---

## Experiment registry

Full measured search: [`results/resubmission/experiments.json`](results/resubmission/experiments.json)

- **Baseline** (EN 3 · HI 4 · TE 4 · BN 2): final grade **3495.28**
- **Winner** (EN 2 · HI 3 · TE 6 · BN 4): final grade **19867.44**
- ~300+ real tokenizers trained in coarse grid + neighbor refinement

---

## Legacy (not resubmission)

The original custom JSON BPE (`results/tokenizer.json`, score **2002.10** on plain-text corpora) is preserved for research history. It is **not** the evaluator-compatible result. See `results/pre_resubmission_snapshot.json` for why the first submission scored **49.9/1000**.

---

## Limitations

- Benchmark is four frozen Wikipedia India pages only.
- Faithful Markdown corpus may differ slightly from a reference builder unless byte-identical.
- Weight search is bounded grid + local neighbors — not a claim of global optimality.
- Legacy playground UI still loads the custom tokenizer for research demos.

## License

MIT
