# ADR-003: Indic Four-Tier Split

**Status:** Accepted  
**Date:** 2026-08-01  
**DDL:** DDL-005 through DDL-008

## Context

Session 5 forbids hiding Indic behind a single headline number. Inventory has heterogeneous provenance: licensed gov (verified), MCDA web crawl (unverified), parallel corpora (translated), verifier-passed synth.

## Decision

Within the 237.6B Indic lane:

| Tier | % | Tokens (B) | Supply reality |
|------|--:|----------:|----------------|
| Verified | 35 | 83.2 | 12B raw → 6.9× repeat |
| Unverified | 40 | 95.0 | 420B crawl → 0.23× (abundant) |
| Translated | 15 | 35.6 | 45B parallel → 0.79× |
| Synthetic | 10 | 23.8 | 8B verified synth → 2.98× |

Global synthetic cap remains 6% (72B) per M6 matrix.

## Consequences

- Reviewer can audit each tier independently
- Unverified is largest tier because supply is real, not because we prefer it
- Verified tier requires cleaning sprint on gov/NCERT packs (Session 4 pipeline extended)
