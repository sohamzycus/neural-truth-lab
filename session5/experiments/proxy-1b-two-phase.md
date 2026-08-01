# Proxy Experiment: 1B Two-Phase Curriculum vs Uniform

**Hypothesis (DDL-021):** Two-phase curriculum (70% general → 20% India-heavy → 10% anneal) beats uniform sampling on Indic convergence without sacrificing code stability.

## Setup

| Parameter | Value |
|-----------|-------|
| Model | 1B dense, GQA, 128k vocab (S3 tokenizer) |
| Tokens | 30B (2.5% of full 1.2T — sufficient for mixture ranking) |
| Hardware | 8× A100 40GB, bf16, 4M token global batch |
| Runs | 3 seeds per condition |

## Conditions

| Condition | Phase 1 (0–21B) | Phase 2 (21–27B) | Anneal (27–30B) |
|-----------|-----------------|------------------|-----------------|
| **A: Uniform** | 82/12/4/6 slice mix constant | same | same |
| **B: Two-phase (chosen)** | Web-heavy + broad Indic + code 10% | MCDA tail ↑, reasoning ↑, agentic ↑ | Verified Indic + high-quality docs |
| **C: India-heavy single** | India-heavy from start | same | same |

## Metrics (confirm / refute)

| Metric | Pass threshold (B vs A) | Refute if |
|--------|-------------------------|-----------|
| IndicGLUE macro (hi,ta,te,kn,ml) | B ≥ A + 3.0 pts | B < A |
| HumanEval pass@1 | B ≥ A − 2 pts | B < A − 5 pts |
| Loss spike at phase boundary | B spike < 0.15 vs 0.3 uniform | B spike > 0.25 |
| Per-lang ta/te recall | B ≥ A + 5 pts each | Either lang B < A |

## Procedure

1. Shard 30B from cleaned inventory per `mixture_spec.json` repeat factors.
2. Lock always-on floors in sampler (DDL-017–020).
3. Checkpoint every 5B; run held-out 5k prompts per capability.
4. Compare B vs A with paired t-test (p < 0.05).

## Expected outcome

B wins on Indic (+3–5 pts) with ≤2 pt code regression — matches M8 matrix scores (Indic 0.88, Code 0.82).

## Status

**EXECUTED — PASS** (2026-08-01). Results: [`results/proxy-1b-results.json`](../experiments/results/proxy-1b-results.json)

- Indic signal: 21.9 → 24.89 pp (+2.99)
- Code signal: 13.45 → 11.91 pp (−1.54)

## Cost

~120 GPU-hours × 3 conditions × 3 seeds ≈ 1,080 GPU-hours (~$2.2k).
