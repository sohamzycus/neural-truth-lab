# ADR-001: Capability Lane Allocation

**Status:** Accepted  
**Date:** 2026-08-01  
**DDL:** DDL-003 through DDL-016

## Context

Session 3 locked 1.2T tokens at 82/12/4/6 (NL/code/math/synthetic). Session 5 requires explicit capability lanes with benchmark traceability, Indic tier splits, and agentic/reasoning/long-context slots.

## Decision

Split the **1,080B active pretrain budget** (90%) across 10 capability lanes totaling 100%. Hold **120B (10%)** as anneal reserve outside the selector.

| Lane | % | Tokens (B) |
|------|--:|----------:|
| Web & General NL | 38 | 410.4 |
| Indic Multilingual | 22 | 237.6 |
| Code | 10 | 108.0 |
| STEM | 8 | 86.4 |
| Reasoning | 6 | 64.8 |
| Agentic | 4 | 43.2 |
| Long Context | 3 | 32.4 |
| Conversation & Code-Switch | 5 | 54.0 |
| Planning | 2 | 21.6 |
| Domain (Ataavi) | 2 | 21.6 |

Code reduced from 12%→10% to fund explicit reasoning (6%) and agentic (4%) lanes required by Session 5.

## Consequences

- Every lane maps to benchmarks in `eval_hierarchy.json`
- Supply gaps documented with `repeat_factor` — no silent wishful accounting
- Ataavi lane honest about 5400× repeat until cleaning sprint completes
