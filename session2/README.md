# SamaBPE

**How should four languages share just 10,000 tokens?**

SamaBPE explores how English, Hindi, Telugu and Bengali can share one constrained 10,000-token BPE vocabulary. Hugging Face provides the standard BPE engine. SamaBPE adds a multilingual exposure-search layer that trains and measures real tokenizer candidates to find a better balance across all four languages.

**Production:** https://sama-bpe-tokenizer-413.netlify.app  
**Repository:** [neural-truth-lab/session2](https://github.com/sohamzycus/neural-truth-lab/tree/main/session2)

---

## The Challenge

| Constraint | Value |
| ---------- | ----- |
| Corpora | India's Wikipedia page in four languages |
| Languages | English (`en`), Hindi (`hi`), Telugu (`te`), Bengali (`bn`) |
| Tokenizer | One shared tokenizer |
| Vocabulary | Maximum 10,000 entries |
| Routing | No per-language tokenizer; no runtime language routing |

All four languages compete for the same merge slots in one vocabulary.

## What Hugging Face BPE Does

Hugging Face `tokenizers` implements byte-pair encoding: start from characters, iteratively merge the most frequent adjacent pairs until the vocabulary budget is reached. This submission uses:

- **Model:** BPE
- **Normalizer:** NFKC
- **Pretokenizer:** Metaspace (`▁`, `prepend_scheme=never`)
- **Decoder:** Metaspace

The trainer learns subword merges from whatever text exposure it receives.

## What SamaBPE Adds

```text
Frozen Wikipedia snapshots
        ↓
Choose multilingual exposure weights
        ↓
Train real Hugging Face BPE
        ↓
Validate lossless round-trip
        ↓
Measure all four languages
        ↓
Compare multilingual balance
        ↓
Adjust weights
        ↓
Repeat
        ↓
Best measured valid candidate wins
```

> SamaBPE does not replace or modify the Hugging Face BPE algorithm. It optimizes the multilingual training exposure supplied to the standard trainer.

> Training weights influence which characters, subwords and merges compete for the shared vocabulary. They do not create fixed per-language token quotas.

## Corpus

Authoritative evaluation corpora: `submission/corpus/{lang}.faithful.txt` (`.faithful.md` is byte-identical).

| Lang | Article | Path | SHA-256 (prefix) | Eval units | Revision |
| ---- | ------- | ---- | ---------------- | ---------: | -------- |
| English | India | `submission/corpus/en.faithful.txt` | `beefe609575008bc…` | 147,908 | 1363833574 |
| Hindi | भारत | `submission/corpus/hi.faithful.txt` | `e7faf48f3010e942…` | 67,473 | 6579409 |
| Telugu | భారతదేశం | `submission/corpus/te.faithful.txt` | `d0f5727be7ea9167…` | 27,225 | 4848340 |
| Bengali | ভারত | `submission/corpus/bn.faithful.txt` | `be103ace9d5d2ada…` | 68,468 | 9043433 |

Builder: `scripts/build_wiki_faithful_markdown.py` · Metadata: `submission/corpus/{lang}.meta.json`

## Baseline

Standard HF BPE at weights **EN 3 · HI 4 · TE 4 · BN 2** (`results/resubmission/baseline/tokenizer.json`).

| Lang | Fertility |
| ---- | --------: |
| EN | 0.7985 |
| HI | 0.7960 |
| TE | 0.9377 |
| BN | 0.9336 |

Spread **0.1417** · Calculated self-score **7,057.31** · EN & HI &lt; 1.2: PASS

## SamaBPE Search

Implemented in `scripts/run_faithful_weight_search.py` with `python/samabpe/weight_optimizer.py` and `python/samabpe/hf_bpe_trainer.py`.

| Stage | Behavior |
| ----- | -------- |
| Search space | Integer weights `(en, hi, te, bn)` with canonical deduplication by GCD |
| Candidate generation | Grid sweep + neighbor refinement |
| Training | Real `BpeTrainer`, vocab cap 10,000 |
| Validation | Lossless `decode(encode(text))` on reviewer sample + four full corpora |
| Ranking | Minimize spread; require EN & HI &lt; 1.2; tie-break on adjusted self-score |
| Stopping | Full measured grid under NFKC+Metaspace |

## Experiment Integrity

Machine-verified counts in `results/final-experiment-integrity.json`:

| Check | Count |
| ----- | ----: |
| Total registry records | 2,570 |
| Hugging Face BPE runs | 2,570 |
| Unique weight configurations | 2,570 |
| NFKC + Metaspace | 2,570 |
| Four-language corpora | 2,570 |
| Passed lossless round-trip | 2,570 |
| Passed EN & HI &lt; 1.2 | 2,570 |

**2,570 real Hugging Face BPE candidates trained and measured** — verified; legacy experiments are not mixed into this registry.

## Final Winner

| Field | Value |
| ----- | ----- |
| Weights | EN 3 · HI 5 · TE 9 · BN 5 |
| Experiment ID | `faithful-hf-2361` |
| Vocabulary | 10,000 |
| Tokenizer SHA-256 | `9f80405daa8f9a6b1832462bf970d9ff390b7f12c19eaa370ca80002d0fc00b5` |

| Lang | Fertility |
| ---- | --------: |
| EN | 0.8532 |
| HI | 0.8297 |
| TE | 0.8447 |
| BN | 0.8487 |

Spread **0.0234** · Raw score **42,650.36** · Hindi penalty **1.0** · Calculated self-score **42,650.36**

This is a reproducible self-calculated metric — not an official awarded grade.

## Baseline vs SamaBPE Winner

Source: `results/final-baseline-vs-winner.json` (fresh evaluation on identical corpora).

| Metric | Baseline HF BPE | SamaBPE Winner | Change |
| ------ | --------------: | -------------: | -----: |
| English fertility | 0.7985 | 0.8532 | +0.0547 |
| Hindi fertility | 0.7960 | 0.8297 | +0.0337 |
| Telugu fertility | 0.9377 | 0.8447 | −0.0930 |
| Bengali fertility | 0.9336 | 0.8487 | −0.0849 |
| Spread | 0.1417 | 0.0234 | −0.1183 (**83.5% reduction**) |
| Self-score | 7,057.31 | 42,650.36 | +35,593 |

Spread tightened by **83.5%** (0.1417 → 0.0234). SamaBPE accepts a measured trade-off in English and Hindi fertility to significantly improve Telugu and Bengali and reduce overall multilingual fertility spread.

## Inside the 10K Vocabulary

Source: `results/final-vocabulary-analysis.json` — vocabulary composition by script (not language ownership).

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

> Script composition is not language ownership. Latin tokens may appear in URLs across every corpus, while punctuation, digits and Markdown symbols are naturally shared.

## Vocabulary Utilization

Source: `results/final-vocabulary-utilization.json` — measured by encoding each frozen corpus with the submitted tokenizer.

| Corpus | Unique token IDs |
| ------ | ---------------: |
| EN | 4,331 |
| HI | 4,124 |
| TE | 3,220 |
| BN | 4,531 |

| Overlap | Count |
| ------- | ----: |
| Used by ≥1 corpus | 9,211 |
| Unused by all four | 789 |
| Used by exactly one | 5,619 |
| Used by exactly two | 1,399 |
| Used by exactly three | 1,101 |
| Used by all four | 1,092 |

> These sets overlap. A vocabulary entry can be used by multiple corpora, so per-language usage counts do not add up to 10,000.

## Try the Encoder

```bash
cd submission
python encoder.py "India भारत తెలుగు বাংলা"
```

Web playground: https://sama-bpe-tokenizer-413.netlify.app/#try-it

## Reproduce in 3 Steps

### Step 1 — Get the exact corpus

Frozen snapshots in `submission/corpus/` for EN, HI, TE, BN.

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

Expected output (reproduced from clean-room test):

```text
English   fertility: 0.8529491305406063
Hindi     fertility: 0.8296355579268745
Telugu    fertility: 0.84455463728191
Bengali   fertility: 0.8485715954898638

Spread: 0.023313572613731792
Adjusted self-score: 42893.46882043277
```

Regenerate all gate artifacts:

```bash
python scripts/run_final_submission_gate.py
```

## Submission Package

| File | Present |
| ---- | ------- |
| `submission/tokenizer.json` | ✓ |
| `submission/encoder.py` | ✓ |
| `submission/evaluate_tokenizer.py` | ✓ |
| `submission/evaluator_contract.py` | ✓ |
| `submission/build_wiki_faithful_markdown.py` | ✓ |
| `submission/train_tokenizer.py` | ✓ |
| `submission/metrics.json` | ✓ |
| `submission/provenance.json` | ✓ |
| `submission/requirements.txt` | ✓ |
| `submission/README.md` | ✓ |
| `submission/corpus/` | ✓ |

## Code Map

| File | Purpose | Final submission? |
| ---- | ------- | ----------------- |
| `submission/tokenizer.json` | Final shared 10K tokenizer | Yes |
| `submission/evaluate_tokenizer.py` | Standalone reproduction evaluator | Yes |
| `submission/encoder.py` | CLI encode/decode | Yes |
| `submission/evaluator_contract.py` | Evaluation units + scoring | Yes |
| `submission/corpus/` | Frozen Wikipedia snapshots | Yes |
| `python/samabpe/hf_bpe_trainer.py` | HF BPE training (NFKC+Metaspace) | Yes (training) |
| `python/samabpe/weight_optimizer.py` | Weight grid + neighbor search | Yes (search) |
| `scripts/run_faithful_weight_search.py` | Search orchestrator | Yes (search) |
| `scripts/build_wiki_faithful_markdown.py` | Corpus builder | Yes (corpus) |
| `python/samabpe/submission_audit.py` | Audit + verified data builder | Yes (verification) |
| `scripts/run_final_submission_gate.py` | Final gate + all evidence JSON | Yes (verification) |
| `scripts/generate_verified_submission_data.py` | UI JSON (subset; gate is canonical) | Yes (UI) |
| `results/resubmission/experiments.json` | Experiment registry | Yes (evidence) |
| `results/final-experiment-integrity.json` | Machine-verified experiment counts | Yes (evidence) |
| `results/final-baseline-vs-winner.json` | Baseline comparison | Yes (evidence) |
| `results/final-vocabulary-analysis.json` | 10K script composition | Yes (evidence) |
| `results/final-vocabulary-utilization.json` | Corpus token usage | Yes (evidence) |
| `results/final-artifact-parity.json` | Tokenizer/corpus SHA parity | Yes (evidence) |
| `results/final-playground-parity.json` | Python vs browser parity | Yes (evidence) |
| `web/public/data/verifiedSubmission.json` | Frontend source of truth | Yes (UI) |
| `web/src/components/ResearchStory.tsx` | Main product story | Yes (UI) |
| `web/src/lib/hf-encoder.ts` | Browser tokenizer parity | Yes (UI) |
| `results/resubmission/baseline/tokenizer.json` | Baseline artifact | Yes (comparison) |
| `python/samabpe/bpe.py`, `hf_bpe.py` | Legacy/custom BPE research | No |
| `results/tokenizer.json` (root results) | Pre-resubmission research | No |

## Evaluation Methodology

**Evaluation units** (wiki-faithful Markdown denominator): contiguous Unicode letter/mark/number runs OR individual visible non-whitespace punctuation/symbol — `[\p{L}\p{M}\p{N}]+|[^\s\p{L}\p{M}\p{N}]`.

**Fertility** = encoded tokens ÷ evaluation units (per language).

**Spread** = max fertility − min fertility across EN/HI/TE/BN.

**Raw score** = 1000 ÷ spread.

**Hindi penalty** = exp(max(0, hindi_fertility / 1.2 − 1)).

**Adjusted self-score** = raw score ÷ Hindi penalty.

**Text preservation:** `decode(encode(text))` must preserve visible non-whitespace characters (NFKC-normalized for full corpora).

## Limitations

- Bounded integer weight search — not a global continuous optimum
- Results depend on specific frozen Wikipedia revisions and HTML→Markdown pipeline
- Script classification describes token shape, not language ownership
- 789 vocabulary entries unused by all four evaluation corpora
- Isolated stress strings with rare symbols may fail round-trip; four full corpora pass
- NFKC normalizer means strict literal round-trip may differ for NFKC-equivalent characters (e.g. `…` → `...`, `″` → `′′`); evaluator uses NFKC-visible comparison
- Final submission tokenizer is a hardened retrain at winner weights (see `provenance.json` → `hardening`)

## Legacy Research History

Earlier experiments used NFKC with punctuation stripping, Whitespace pretokenizer, word-ish denominators, and custom JSON BPE. That pipeline failed visible-text preservation on the reviewer sample and is **not** the current submission.

Artifacts under `results/` from pre-resubmission work (~2,971 earlier runs, Maithili explorations, custom encoders) are research history only. Do not mix their counts with the 2,570 NFKC+Metaspace measurements in `results/resubmission/experiments.json`.

---

## License

MIT
