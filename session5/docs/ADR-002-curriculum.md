# ADR-002: Two-Phase Curriculum with Anneal Reserve

**Status:** Accepted  
**Date:** 2026-08-01  
**DDL:** DDL-001, DDL-002, DDL-021

## Context

M8 matrix (Session 3) ranked two-phase curriculum highest on Indic convergence (0.88) and eval generalization (0.85). Session 5 requires explicit anneal reserve and smooth transitions.

## Decision

| Phase | % of 1.2T | Tokens (B) | Months | Emphasis |
|-------|----------:|-----------:|--------|----------|
| Phase 1 | 70% | 840 | 1–12 | Web, broad Indic, code, STEM |
| Phase 2 | 20% | 240 | 10–14 | India-heavy, reasoning, agentic, LC ramp |
| Anneal | 10% | 120 | 14–15 | Verified Indic, high-quality docs, LR decay |

Phase 2 begins with 20B token linear ramp (not step change) to avoid F-006 loss spike.

## Consequences

- Anneal reserve locked in sampler until month 14
- Context length: 4k (P1) → 8k (P2 early) → 16k (P2 mid) → 32k (P2 late + anneal)
- Rejected: dynamic mixture (wall-clock 0.60), single-phase India-heavy (code stability 0.75)
