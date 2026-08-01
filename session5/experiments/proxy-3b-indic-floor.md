# Proxy Experiment: 3B Indic Floor + Long-Context Ramp

**Hypothesis (DDL-017, DDL-022):** Always-on Indic floor (18%) plus 4k→32k context curriculum prevents tail-language collapse and needle recall failure at 3B scale.

## Reproducibility Protocol

| Field | Specification |
|-------|---------------|
| **Hypothesis** | Floors + LC ramp prevent tail-lang and needle collapse vs OPUS-free baseline |
| **Independent variables** | Indic floor 18% on/off; context ramp 4k→32k on/off; agentic floor 3% |
| **Controls** | Condition A: no floors, fixed 4k; same 3B arch and 90B token budget |
| **Dependent metrics** | Lang tail proxy (pp); needle proxy @32k; agent recovery proxy |
| **Acceptance criteria** | Tail Δ ≥ +4.0pp; needle ≥ 0.75; grad-norm instability = 0 |
| **Failure criteria** | Needle < 0.55 OR tail Δ < +2.0pp OR >2 grad-norm events |
| **Decision rule** | PASS → keep floors §14 + context ramp §13; FAIL → raise floor to 20% and re-proxy |
| **Follow-up** | Full 1B GPU 30B tokens with real IndicGLUE; needle@32k on legal held-out |

## Setup

| Parameter | Value |
|-----------|-------|
| Model | 3B dense, GQA, 128k vocab |
| Tokens | 90B (7.5% of full pretrain) |
| Context curriculum | 4k (0–30B) → 8k (30–60B) → 16k (60–80B) → 32k (80–90B) |

## Conditions

| Condition | Indic floor | Context ramp | Agentic floor |
|-----------|-------------|--------------|---------------|
| **A: No floors** | OPUS free | Fixed 4k | OPUS free |
| **B: Floors only** | 18% min | Fixed 4k | 3% min |
| **C: Floors + ramp (chosen)** | 18% min | 4k→32k | 3% min |

## Metrics

| Metric | Pass (C vs A) | Refute if |
|--------|---------------|-----------|
| IndicGLUE ta/te/ml | C ≥ A + 4 pts | C < A |
| Needle recall @32k | C ≥ 0.75 | C < 0.55 |
| Agent tool-call accuracy | C ≥ A + 5 pts | C < A |
| Indic-Faithfulness | C ≥ 0.78 | C < 0.72 |
| Training instability (grad norm >10×) | C: 0 events | C: >2 events |

## Indic tier ablation (secondary)

Within condition C, compare tier mixes at 90B:

| Tier mix | Verified | Unverified | Translated | Synthetic |
|----------|----------|------------|------------|-----------|
| C1 (chosen) | 35% | 40% | 15% | 10% |
| C2 (synth-heavy) | 30% | 35% | 15% | 20% |
| C3 (verified-heavy) | 50% | 30% | 15% | 5% |

**Metric:** Indic-Faithfulness — C1 should beat C2 by ≥0.04 (validates DDL-008 synth cap).

## Status

**EXECUTED — PASS** (2026-08-01). Results: [`results/proxy-3b-results.json`](../experiments/results/proxy-3b-results.json)

- Lang tail proxy: 12.87 → 17.39 (+4.52)
- Needle proxy: 0.548 → 0.777

## Cost

~2,400 GPU-hours (~$4.8k).
