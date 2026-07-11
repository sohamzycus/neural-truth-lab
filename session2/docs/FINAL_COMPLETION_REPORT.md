# Final Optimization Pass — Completion Report

## 1. Executive result

The verified score was **not improved** by the final boundary-aware weight search. The pre-final baseline tokenizer (weighted shared BPE, score **1651.59**) remains the authoritative submission. Four corpus-weight perturbations were materialized and freshly verified; none beat the baseline without violating constraints. All constraints still pass. The final tokenizer is byte-identical to the pre-final baseline.

## 2. Baseline vs final

| Metric | Pre-final baseline | Final | Change |
|--------|-------------------|-------|--------|
| Vocabulary size | 10,000 | 10,000 | 0 |
| English tokens | 10,622 | 10,622 | 0 |
| English X | 1.0495 | 1.0495 | 0 |
| Hindi tokens | 10,672 | 10,672 | 0 |
| Hindi X | 1.3211 | 1.3211 | 0 |
| Telugu tokens | 3,271 | 3,271 | 0 |
| Telugu X | 1.3027 | 1.3027 | 0 |
| Bengali tokens | 10,572 | 10,572 | 0 |
| Bengali X | 1.6550 | 1.6550 | 0 |
| Fairness gap | 0.605477 | 0.605477 | 0 |
| Verified self-score | 1651.59 | 1651.59 | 0 |

## 3. Score search evidence

- **Initial X_min / X_max:** English / Bengali
- **Final X_min / X_max:** English / Bengali (unchanged)
- **Algorithms attempted:** corpus weight perturbation (4 materialized candidates)
- **Candidates accepted:** 0
- **Best individual improvement:** none (baseline retained)
- **Boundary transitions:** none
- **Vocabulary ROI:** guided analysis; no verified merge rebuild accepted
- **Deliberate degradation explored:** no (Track B not used)
- **Deliberate degradation in final tokenizer:** NO

## 4. Final verified result

- **Tokenizer:** `results/tokenizer.json`
- **Vocabulary:** 10,000
- **Score:** 1651.590272242215
- **Gap:** 0.6054770464604338
- **English constraint:** PASS (X ≤ 1.2)
- **One-tokenizer proof:** VERIFIED (`one_tokenizer_proof.json`)
- **Mixed-script:** VERIFIED

## 5. Optimization claim

**Level 3** — Score-aware vocabulary allocation via weighted shared BPE with English seed and Indic pair weighting. Level 4 (direct score-aware merge selection) is implemented in `train_score_directed_adaptive` but did not win the verified strategy comparison.

## 6. Authenticity proof

- **Tokenizer SHA-256:** `6415894d3bac446b81013a9378a5c2fc8265f1db5947e579e2859bb65fe3ffda`
- **Verification:** `python scripts/verify.py`
- **Download hash match:** verified via `artefact_proof.json`

## 7. UI changes

- Manrope primary UI font; Noto Devanagari/Telugu/Bengali for script labels
- Hero: clamp() typography, tabular numerals, X_min/X_max labels
- Denominator expandable near score
- One-tokenizer mixed-script proof in hero
- Strategy arena: Vanilla vs Final foregrounded
- Verification section compact; grapheme/budget sim demoted

## 8. Tests executed

| Command | Result |
|---------|--------|
| `pytest python/tests -q` | PASS (29) |
| `npm test` (web) | PASS (3) |
| `npm run build:netlify` | PASS |
| `python scripts/verify.py` | PASS |
| `python scripts/final_analysis.py` | PASS |
| `python scripts/final_score_search.py` | PASS (no improvement) |

## 9. Remaining risks

- Weight grid is local (4 points); broader search may find marginal gains at high compute cost
- At 10K vocab, single-merge ROI headroom is limited per `score_roi_candidates.json`
- Denominator interpretation remains documented in `docs/DENOMINATOR.md` for evaluator alignment
