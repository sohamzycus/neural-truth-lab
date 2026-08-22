# Session 8 — Pre-Implementation Audit

**Date:** 2026-08-22  
**Scope:** `session8/` directory in ERA V5 monorepo

## Repository State

`session8/` was **empty** at audit time — no existing application, no `package.json`, no components, no data model, no README. This is a **greenfield build**, not a refactor.

## Current Strengths

- None in-session. Adjacent sessions (`session4/web`, `session7/app`) demonstrate strong visual/interactive patterns in this monorepo that we can learn from without copying.

## Current Weaknesses

- No application exists.
- No chronology data.
- No interactive experiments.
- No deployment configuration.
- No source audit trail.

## Technical Inaccuracies

- N/A (no prior content).

## UX Problems

- N/A (no prior content).

## Storytelling Problems

- N/A (no prior content).

## Missing Mechanisms (must build)

All assignment-required mechanisms: Bahdanau, scaled dot-product, MHA, positional encodings (learned, sinusoidal, RoPE, ALiBi, DroPE), Transformer-XL, sparse family (Sparse Transformer, Longformer, BigBird, Top-k, NSA), MQA/GQA/MLA, FlashAttention, linear/DeltaNet/Gated DeltaNet, attention sinks/StreamingLLM, context extension (PI, NTK-aware, YaRN), sliding window, FlashAttention IO story.

## Missing Experiments (must build)

- Opening attention pipeline (Q×Kᵀ → softmax → weighted V)
- Q/K/V interactive experiment with "bank" disambiguation
- Causal masking toggle
- O(n²) sequence-length slider with matrix growth
- KV cache decoding simulator (MHA/GQA/MQA)
- RoPE rotation visualization
- DeltaNet toy associative memory
- MLA compression story
- Attention sinks streaming demo
- Architecture builder lab
- Scenario reasoning game
- 60-second guided tour
- Beginner/Expert mode

## Missing Chronology Evidence

- Entire primary-source chronology table (`src/data/chronology.ts`) must be created with verified dates and source types.

## Visual Opportunities

- Deep-space laboratory aesthetic (distinct from session4's corpus-green palette — use cosmic indigo/cyan/violet)
- Token nodes as luminous probes; attention as connection strength; KV cache as memory reservoirs
- Timeline as primary navigation spine
- Canvas-based attention matrices for performance at scale
- Pressure indicators (QUALITY / COMPUTE / MEMORY / CONTEXT / LATENCY) animating with era

## Benchmark Reference

The provided Replit benchmark (`realistic-awesome-exponent--deepjyotisaha2.replit.app`) was unreachable during audit (fetch timeout). Design target remains: **beat it** on polish, rigor, interactivity, and causal storytelling.

## Implementation Decision

Radical greenfield build under `session8/web/` using Vite + React + TypeScript + Tailwind + Framer Motion, following monorepo conventions from `session4/web`.
