<!--
Sync Impact Report
Version change: none → 1.0.0
Added: SamaBPE project constitution (initial)
Templates: specs, plan, tasks aligned
-->

# SamaBPE Constitution

**Version:** 1.0.0  
**Ratified:** 2026-07-11  
**Last Amended:** 2026-07-11

## Mission

Build a deterministic, independently verifiable BPE tokenizer that maximizes multilingual fertility fairness across four Wikipedia India articles under a 10,000-token vocabulary budget.

## Principles

### P1 — Measured Truth

Every displayed metric MUST originate from generated artefacts. Never hard-code fertility, scores, or allocations. Distinguish measured, predicted, and illustrative data in UI and docs.

### P2 — Reproducibility

Corpora are frozen with SHA-256 hashes. `scripts/verify.py` is the single source of truth for headline scores. The React UI reads `results/stats.json` only.

### P3 — Test-First Core Logic

Word-unit counting, BPE encode/decode, and verification assertions are developed test-first. No production logic without a failing test observed first.

### P4 — Determinism

Tokenizer training uses fixed seeds, stable sort orders, and documented pretokenization. Identical inputs produce identical `tokenizer.json`.

### P5 — Constraint Integrity

English fertility X_en MUST be ≤ 1.2. Vocabulary size MUST be ≤ 10,000. Winning strategy is selected only from verified benchmark results.

### P6 — Unicode Correctness

NFC normalization and extended grapheme clusters (`\X`) are used where appropriate. Grapheme Integrity Score is measured and exposed.

### P7 — Minimal Surface

Prefer deletion over addition. Reuse shared modules. One verification path, one stats schema, one tokenizer export format.

## Governance

Amendments require updating this file with version bump and sync impact report. Implementation plans and specs must reference active constitution version.
