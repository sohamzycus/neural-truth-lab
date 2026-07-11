# SamaBPE Final Optimization Plan — Implementation Spec

Source: `SamaBPE Final Optimization Plan.docx` (ERA V5 Session 2, final surgical pass).

## Objective

Improve verified assignment score only through legitimate measured changes; strengthen proof chain and first-viewport clarity. No fabricated metrics.

## Priority order

1. Freeze verified baseline (`pre_final_baseline.json`)
2. Boundary-aware score search (Track A)
3. Fresh verification + artefact sync
4. UI: challenge → result → meaning → proof in ~10s
5. Typography (Manrope + Noto scripts), denominator visibility, section reprioritization

## Artefacts

| File | Phase | Purpose |
|------|-------|---------|
| `pre_final_baseline.json` | 1 | Immutable snapshot before final optimization |
| `boundary_analysis.json` | 3 | Integer token sensitivity per language |
| `score_target_ladder.json` | 4 | Hypothetical savings from X_max |
| `one_tokenizer_proof.json` | 5, 18 | Mixed-script single-tokenizer evidence |
| `token_overhead_analysis.json` | 6 | Top overhead words in X_max language |
| `vocabulary_efficiency_audit.json` | 8 | 10K vocab usage audit |
| `final_score_search_trace.json` | 9–12 | Materialized weight-search trace |
| `score_roi_candidates.json` | 7 | ROI candidates (existing pipeline) |

## Scripts

```bash
python scripts/verify.py              # baseline + stats + pre_final_baseline
python scripts/final_analysis.py      # phases 3–8 analysis
python scripts/final_score_search.py  # boundary-aware weight search
python scripts/verify.py              # re-verify if tokenizer changed
python scripts/score_analysis.py      # ROI + optimization audit
pytest python/tests -q
cd web && npm run build:netlify
```

## Score math (non-negotiable)

- `X = encoded_tokens / word_units` (integers → full-precision float)
- `gap = X_max − X_min` (full precision)
- `score = 1000 / gap`
- Display rounding never feeds back into scoring

## Optimization claim levels

- **Level 3** (current): score-aware vocabulary allocation via weighted shared BPE
- **Level 4**: direct score-aware merge selection (only if verified winner uses it)

## Track A vs B

- **Track A** (primary): compression-honest; no deliberate X_min degradation
- **Track B**: sensitivity experiment only; not used in final tokenizer unless explicitly chosen

## UI acceptance

- First viewport: 4 X values, fairness gap bar, verified score dominant
- Denominator explanation adjacent to score
- One-tokenizer proof near hero
- Strategy arena: Vanilla vs Final foreground
- Secondary sections (grapheme, budget sim) deprioritized visually

## Deploy

Prebuilt `web/dist/` committed; GitHub Actions workflow `netlify-deploy.yml` on push to `main`.
