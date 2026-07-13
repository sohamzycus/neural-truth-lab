# SamaBPE

**Production:** https://sama-bpe-tokenizer-413.netlify.app  
**Repository:** [neural-truth-lab/session2](https://github.com/sohamzycus/neural-truth-lab/tree/main/session2)

## 1. SamaBPE

SamaBPE explores a simple question: when English, Hindi, Telugu and Bengali must share one 10,000-token BPE vocabulary, how should their relative training exposure be balanced?

Hugging Face provides the standard BPE implementation (`tokenizers` library). SamaBPE adds a multilingual exposure-search layer: it systematically varies how much each language contributes to training, trains real Hugging Face BPE candidates, evaluates every valid candidate on the same four frozen Wikipedia snapshots, and selects the strongest four-language balance.

## 2. The challenge

| Constraint | Value |
| ---------- | ----- |
| Languages | English (`en`), Hindi (`hi`), Telugu (`te`), Bengali (`bn`) |
| Corpora | India's Wikipedia article in each language |
| Tokenizer | One shared tokenizer |
| Vocabulary | Maximum 10,000 tokens |
| Engine | Standard Hugging Face BPE |

All four languages compete for the same vocabulary slots. There is no per-language model and no runtime language routing.

## 3. What SamaBPE adds above Hugging Face BPE

A standard BPE trainer learns merges from whatever text exposure it receives. SamaBPE does not modify the BPE algorithm. It searches **training exposure weights** `(w_en, w_hi, w_te, w_bn)` that control how often each frozen corpus is repeated in the mixed training stream.

For each weight configuration:

1. Build a weighted mixed corpus from the four frozen snapshots
2. Train a real Hugging Face BPE tokenizer (NFKC + Metaspace)
3. Gate on lossless `decode(encode(text))` for reviewer samples and all four full corpora
4. Measure fertility on all four languages with the evaluator contract
5. Rank by spread and adjusted self-score among candidates passing EN & HI &lt; 1.2

Weights influence which characters, subwords and merges win merge slots. They do **not** reserve fixed token quotas per language.

## 4. Architecture

```text
Frozen Wikipedia snapshots (en, hi, te, bn)
        ↓
SamaBPE exposure-weight search
        ↓
Real Hugging Face BPE training (NFKC + Metaspace)
        ↓
Lossless text-preservation validation
        ↓
Four-language evaluation
        ↓
Candidate ranking
        ↓
Winner → submission/tokenizer.json
```

## 5. Corpus

Authoritative evaluation corpora live in `submission/corpus/`. The evaluator loads `{lang}.faithful.txt`; `.faithful.md` is byte-identical.

| Lang | Article | Path | Eval units | SHA-256 (prefix) | Wikipedia revision |
| ---- | ------- | ---- | ---------: | ---------------- | ------------------ |
| EN | India | `submission/corpus/en.faithful.txt` | 147,908 | `beefe609575008bc…` | 1363833574 |
| HI | भारत | `submission/corpus/hi.faithful.txt` | 67,473 | `e7faf48f3010e942…` | 6579409 |
| TE | భారతదేశం | `submission/corpus/te.faithful.txt` | 27,225 | `d0f5727be7ea9167…` | 4848340 |
| BN | ভারত | `submission/corpus/bn.faithful.txt` | 68,468 | `be103ace9d5d2ada…` | 9043433 |

Builder: `scripts/build_wiki_faithful_markdown.py`  
Frozen source pack: `data/faithful/`  
Metadata: `submission/corpus/{lang}.meta.json` (revision ID, fetch timestamp, byte counts)

## 6. Baseline

Standard HF BPE trained at weights **EN 3 · HI 4 · TE 4 · BN 2** (`results/resubmission/baseline/tokenizer.json`).

| Lang | Fertility |
| ---- | --------: |
| EN | 0.7985 |
| HI | 0.7960 |
| TE | 0.9377 |
| BN | 0.9336 |

| Metric | Value |
| ------ | ----: |
| Spread | 0.1417 |
| Calculated self-score | 7,057.31 |
| EN & HI &lt; 1.2 | PASS |

Telugu and Bengali were far from English/Hindi balance despite passing individual thresholds.

## 7. Search strategy

Implemented in `scripts/run_faithful_weight_search.py` with helpers in `python/samabpe/weight_optimizer.py` and `python/samabpe/hf_bpe_trainer.py`.

- **Search space:** Integer weight grid with deduplication by `(en, hi, te, bn)` key
- **Candidate generation:** Grid sweep plus neighbor refinement around promising regions
- **Training:** `train_hf_bpe()` — Hugging Face `BpeTrainer`, vocab cap 10,000
- **Validation:** Lossless round-trip on reviewer punctuation sample + four full corpora
- **Ranking:** Minimize spread; tie-break on adjusted self-score; require EN & HI fertility &lt; 1.2
- **Stopping:** Full measured grid under current architecture (2,570 unique configs)

## 8. Experiment integrity

Registry: `results/resubmission/experiments.json` (`architecture: NFKC+Metaspace`)

| Stage | Count | Notes |
| ----- | ----: | ----- |
| Candidates trained | 2,570 | All `huggingface-bpe`, all unique weight configs |
| Valid measured | 2,570 | Status `VALID_MEASURED` |
| Passed lossless round-trip | 2,570 | Reviewer + 4 full corpora |
| Passed EN &lt; 1.2 | 2,570 | |
| Passed HI &lt; 1.2 | 2,570 | |
| Winner | 1 | `faithful-hf-2361` |

Legacy experiments (NFKC + Whitespace, custom JSON BPE, ~2,971 earlier runs) are **not** in this registry. Headline counts refer only to the current architecture.

Audit: `results/final-product-audit.md`

## 9. Final winner

| Field | Value |
| ----- | ----- |
| Weights | EN 3 · HI 5 · TE 9 · BN 5 |
| Experiment ID | `faithful-hf-2361` |
| Tokenizer | `submission/tokenizer.json` |
| SHA-256 | `8d515d68b3ce820dd7fa4b8c31e5e0a19bc7ec9e1f4f982117eaee3f628a0469` |

| Lang | Tokens | Eval units | Fertility |
| ---- | -----: | ---------: | --------: |
| EN | 126,158 | 147,908 | 0.8530 |
| HI | 55,978 | 67,473 | 0.8296 |
| TE | 22,993 | 27,225 | 0.8446 |
| BN | 58,100 | 68,468 | 0.8486 |

| Metric | Value |
| ------ | ----: |
| Spread | 0.0233 |
| Calculated self-score | 42,893.47 |
| EN & HI &lt; 1.2 | PASS |

## 10. Baseline vs winner

| Metric | Baseline | Winner | Change |
| ------ | -------: | -----: | -----: |
| EN fertility | 0.7985 | 0.8530 | +0.0545 |
| HI fertility | 0.7960 | 0.8296 | +0.0336 |
| TE fertility | 0.9377 | 0.8446 | −0.0931 |
| BN fertility | 0.9336 | 0.8486 | −0.0850 |
| Spread | 0.1417 | 0.0233 | −0.1184 |
| Self-score | 7,057.31 | 42,893.47 | +35,836 |

SamaBPE tightened multilingual balance dramatically. English and Hindi fertilities rose slightly; Telugu and Bengali moved much closer to the cluster. Both EN and HI remain below 1.2.

## 11. Inside the 10K vocabulary

Script composition of the winner tokenizer (not language allocation):

| Category | Tokens | % |
| -------- | -----: | -: |
| Latin-dominant | 4,113 | 41.1% |
| Devanagari-dominant | 1,684 | 16.8% |
| Telugu-dominant | 1,478 | 14.8% |
| Bengali-dominant | 1,703 | 17.0% |
| Shared punctuation/digits/symbols | 895 | 9.0% |
| Mixed-script | 113 | 1.1% |
| Other Unicode | 13 | 0.1% |
| Special tokens | 1 | 0.0% |
| **Total** | **10,000** | **100%** |

## 12. Vocabulary utilization

Measured by encoding each frozen corpus with the submitted tokenizer:

| Corpus | Unique token IDs used |
| ------ | --------------------: |
| EN | 4,331 |
| HI | 4,124 |
| TE | 3,220 |
| BN | 4,531 |

| Overlap statistic | Count |
| ----------------- | ----: |
| Used by ≥1 corpus | 9,211 |
| Unused by all four | 789 |
| Used by exactly one | 5,619 |
| Used by all four | 1,092 |

Sets overlap — four per-language counts do not sum to 10,000.

**Baseline → winner vocabulary shift:** increasing Telugu (+446) and Bengali (+550) script-dominant tokens while reducing Latin-dominant (−666) reflects higher TE/BN training exposure.

## 13. Try the encoder

```bash
cd submission
python encoder.py "India भारत తెలుగు বাংলা"
```

Web playground: https://sama-bpe-tokenizer-413.netlify.app/#try-it

## 14. Reproduce in 3 steps

### Step 1 — Get the exact corpus

Frozen India Wikipedia snapshots in `submission/corpus/`.

### Step 2 — Load the exact tokenizer

```python
from tokenizers import Tokenizer
tokenizer = Tokenizer.from_file("tokenizer.json")
```

### Step 3 — Run the evaluator

```bash
cd submission
pip install -r requirements.txt
python evaluate_tokenizer.py
```

Expected output (reproduced 2026-07-13):

```text
English   fertility: 0.8529491305406063
Hindi     fertility: 0.8296355579268745
Telugu    fertility: 0.84455463728191
Bengali   fertility: 0.8485715954898638
Spread: 0.023313572613731792
Adjusted evaluator score: 42893.46882043277
```

Regenerate UI data:

```bash
python scripts/generate_verified_submission_data.py
python scripts/generate_final_product_audit.py
```

## 15. Submission package

| File | Purpose |
| ---- | ------- |
| `submission/tokenizer.json` | Final shared 10K HF BPE tokenizer |
| `submission/corpus/*.faithful.txt` | Frozen evaluation corpora |
| `submission/corpus/*.meta.json` | Corpus provenance |
| `submission/encoder.py` | CLI encode/decode helper |
| `submission/evaluate_tokenizer.py` | Standalone reproduction evaluator |
| `submission/train_tokenizer.py` | Train HF BPE from weighted corpora |
| `submission/metrics.json` | Saved evaluation metrics |
| `submission/provenance.json` | Winner weights and experiment ID |
| `submission/requirements.txt` | Python dependencies |
| `results/resubmission/experiments.json` | Full experiment registry |
| `results/resubmission/baseline/tokenizer.json` | Baseline tokenizer artifact |

## 16. Code map

| File | Purpose |
| ---- | ------- |
| `python/samabpe/hf_bpe_trainer.py` | HF BPE training (NFKC + Metaspace) |
| `python/samabpe/weight_optimizer.py` | Weight grid and neighbor search |
| `python/samabpe/evaluator_contract.py` | Evaluation units, fertility, scoring |
| `python/samabpe/evaluator_text.py` | Text normalization helpers |
| `python/samabpe/submission_audit.py` | Audit, vocab analysis, verified data builder |
| `scripts/run_faithful_weight_search.py` | Main weight search orchestrator |
| `scripts/build_wiki_faithful_markdown.py` | Wikipedia → frozen Markdown corpus |
| `scripts/generate_verified_submission_data.py` | UI source of truth generator |
| `scripts/generate_final_product_audit.py` | Product audit report |
| `scripts/export_playground_parity.py` | Browser/Python parity fixtures |
| `scripts/sync_resubmission_to_web.py` | Copy artifacts to submission/ and web/ |
| `submission/encoder.py` | Submission CLI encoder |
| `submission/evaluate_tokenizer.py` | Submission evaluator |
| `web/src/components/ResearchStory.tsx` | Main product story UI |
| `web/src/lib/hf-encoder.ts` | Browser tokenizer (Metaspace parity) |
| `web/public/data/verifiedSubmission.json` | Authoritative frontend metrics |

## 17. Evaluation methodology

**Evaluation units** (wiki-faithful Markdown denominator): contiguous Unicode letter/mark/number runs plus individual visible symbols — regex `[\p{L}\p{M}\p{N}]+|[^\s\p{L}\p{M}\p{N}]`.

**Fertility** = encoded BPE tokens ÷ evaluation units (per language).

**Spread** = max fertility − min fertility across EN/HI/TE/BN.

**Raw score** = 1000 ÷ spread.

**Hindi penalty** = 0.5 if HI fertility &gt; 1.2, else 1.0.

**Adjusted self-score** = raw score ÷ Hindi penalty.

This is a reproducible self-calculated metric for comparing candidates — not an official awarded grade.

## 18. Limitations

- Bounded integer weight search — not a global continuous optimum
- Results depend on specific frozen Wikipedia revisions and HTML→Markdown pipeline
- Script classification describes token shape, not language ownership
- 789 vocabulary entries unused by all four evaluation corpora
- Isolated stress string with rare symbols (€, @) fails round-trip; full corpora pass
- EN/HI individual fertilities rose vs baseline in exchange for much tighter four-language spread

## 19. Legacy research history

Earlier work used NFKC with punctuation-to-space replacement, Whitespace pretokenizer, word-ish denominators, and a custom JSON BPE encoder. That pipeline failed `decode(encode(text))` on the reviewer sample and is **not** the current submission.

Artifacts under `results/` from pre-resubmission experiments (e.g. `results/tokenizer.json`, strategy sweeps, Maithili explorations) are research history only. Do not mix their experiment counts with the 2,570 NFKC+Metaspace measurements.

---

## License

MIT
