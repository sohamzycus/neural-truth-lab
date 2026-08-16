# ASSIGNMENT SCORECARD (Hardened)

Evidence from `results/summary.json` — regenerate via `python experiments/run_all.py`.

## Problem 3 — Dynamic Kronecker

**PASS** — Dynamic truncation 0% on all language buckets; fixed truncation up to 28.57% (Telugu, baseline corpus).

## Problem 5 — Reversible Embedding

**PARTIAL**
- Deterministic inverse: **100%** (expanded test)
- Learned held-out exact (64-d): **0%** (baseline 6-str and expanded ~46-str test)
- Latent sweep 16–1024-d: **0%** held-out exact at all points

*We do not claim reversible embeddings cannot replace an output head.*

## Problem 4 — Fourier

**PARTIAL** — Magnitude collisions (ab/ba); phase reduces scaled collisions but does not eliminate all.

## New experiments

| Experiment | Status |
|------------|--------|
| Latent capacity sweep | PASS (executed) |
| Decoder ablation | PASS (executed) |
| Scaled collisions (3,408 str) | PASS |
| Expanded train/val/test | PASS |
| Length generalization | PASS |
| Language EN/HI/TE/BN | PASS |
| Parameter accounting | PASS |
| Research webapp | PASS |
| research_check.py | PASS |

## H8 LM

**NOT RUN**

## Reviewer Verdict

Scientifically defensible **partial success** with honest negative results. The project now investigates **where reversibility breaks** rather than claiming victory. Dynamic encoding solves the fixed-window problem; learned inversion from compressed latent **failed under tested conditions** — a publishable boundary result.
