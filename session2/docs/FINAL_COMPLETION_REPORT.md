# Final Submission Hardening — Completion Report

## 1. Executive result

The verified score did **not** improve during this pass. Baseline and final score are both **1651.590272242215**. The fairness gap is unchanged at **0.6054770464604338**. No constraints regressed. Deliberate degradation was **not** used (Track A only). The final tokenizer is independently reproducible via `python scripts/verify.py`.

## 2. Baseline vs final

| Metric | Baseline | Final | Change |
| ------ | -------: | ----: | -----: |
| Vocabulary size | 10,000 | 10,000 | 0 |
| English tokens | 10,622 | 10,622 | 0 |
| English X | 1.0495010374468925 | 1.0495010374468925 | 0 |
| Hindi tokens | 10,672 | 10,672 | 0 |
| Hindi X | 1.321119088883387 | 1.321119088883387 | 0 |
| Telugu tokens | 3,271 | 3,271 | 0 |
| Telugu X | 1.302668259657507 | 1.302668259657507 | 0 |
| Bengali tokens | 10,572 | 10,572 | 0 |
| Bengali X | 1.6549780839073263 | 1.6549780839073263 | 0 |
| Fairness gap | 0.6054770464604338 | 0.6054770464604338 | 0 |
| Verified self-score | 1651.590272242215 | 1651.590272242215 | 0 |

## 3. Score optimization evidence

- **Initial X_min / X_max:** English / Bengali
- **Final X_min / X_max:** English / Bengali
- **Techniques attempted:** corpus-weight perturbation (4 materialized candidates)
- **Accepted candidates:** 0
- **Boundary transitions:** none
- **Vocabulary ROI:** guided analysis; no verified merge accepted
- **Deliberate degradation explored:** NO
- **In final tokenizer:** NO

## 4. Final verified result

- **Tokenizer:** `results/tokenizer.json`
- **Score:** 1651.590272242215 · **Gap:** 0.6054770464604338
- **Constraints:** English PASS · Vocabulary PASS
- **One-tokenizer:** VERIFIED · **Mixed-script:** VERIFIED

## 5. One-tokenizer proof

- One artefact: YES · One vocabulary: YES · One encoding function: YES
- Runtime language routing: NO · Deterministic rerun: PASS · Mixed-script: PASS

## 6. Optimization claim classification

**Level 3** — `train_weighted_shared` in `python/samabpe/strategies.py`. Level 4 implemented but not winning.

## 7. Authenticity proof

- Tokenizer SHA-256: `6415894d3bac446b81013a9378a5c2fc8265f1db5947e579e2859bb65fe3ffda`
- Verification: `python scripts/verify.py`
- Frontend download hash matches: YES (`artefact_proof.json`)

## 8. UI changes

Manrope + Noto fonts; hero shows four ratios → gap → score → proof; denominator expandable; strategy arena foregrounds Vanilla vs Final; secondary sections demoted.

## 9. Tests executed

| Command | Result |
|---------|--------|
| `pytest python/tests -q` | PASS |
| `npm test` | PASS |
| `npm run build:netlify` | PASS |
| `python scripts/verify.py` | PASS |
| `python scripts/final_analysis.py` | PASS |

## 10. Remaining risks

Bounded 4-point weight grid may miss marginal gains; denominator documented in `docs/DENOMINATOR.md`.
