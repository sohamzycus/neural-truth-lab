# ADR-004: Always-On Floors and OPUS

**Status:** Accepted  
**Date:** 2026-08-01  
**DDL:** DDL-017 through DDL-023

## Context

OPUS selects high-utility samples but can starve low-volume high-value lanes (Indic tail, agentic, long-context). Session 5 requires protected floors the selector cannot cross.

## Decision

| Lane | Floor (% of active mix) | Floor (B tokens) |
|------|------------------------:|-----------------:|
| Indic Multilingual | 18% | 194.4 |
| Agentic | 3% | 32.4 |
| Code-Switch | 4% | 43.2 |
| Long Context | 2% | 21.6 |

OPUS utility score weights per-lane benchmark delta proxy. Samples below discard threshold (0.15) are dropped **unless** removal would breach a floor.

## Consequences

- Sampler asserts floor invariants each batch
- OPUS cannot optimize MMLU alone at expense of IndicGLUE ta/te
- Protected lanes may retain lower-utility shards — acceptable tradeoff
