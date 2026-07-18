# V2 Redesign — Consideration Assessment

Assessment of brutal-review gaps and how V2 addresses each.

## Cross-Cutting

| Gap (review) | V2 remediation | Verified by |
|--------------|----------------|-------------|
| Capability-first missing | §1 defines 10 capabilities with SLOs; §3 derives data per capability | `capability_data.json` |
| Sections disconnected | Mandatory upstream/downstream citations in each chapter | Spec 004 spine |
| 12 matrices claimed, 4 present | M1–M12 in `data/inputs/matrices/` | `export_report_data.py` |
| No engineering summary | §0 one-page summary | Report §0 |
| Hindi 21.5% spec typo | Locked at **17.9%** per `language_weights.json` | `verify.py` |

## Assignment Q1 — Data

| Consideration | Assessment | V2 action |
|---------------|------------|-----------|
| Derive from objectives, not lists | **Failed** in V1 | §3 capability→signal→source chain for 11 capability classes |
| Code: repos/PRs/tests | **Partial** V1 | Explicit token budget: repos 42%, docs 18%, issues 12%, SO 10%, tests 8%, RFCs 5%, synth 5% |
| Agentic training recipe | **Failed** V1 | §8 ToolLoop trace formats + 25% post-train allocation |
| India: code-switch, UPI, gov | **Superficial** V1 | Dedicated rows: Hinglish corpus, UPI/GST docs, judiciary PDFs, SME chat |

## Assignment Q2 — Cleaning

| Consideration | Assessment | V2 action |
|---------------|------------|-----------|
| Industrial depth | **Failed** V1 (6 stages) | 16 stages with per-stage yield in `cleaning_pipeline.json` |
| India-specific | **Weak** V1 | L4 Unicode NFC, L14 Indic OCR, L11 instruction leakage for synthetic Hindi |
| Engineering | **Missing** V1 | Composite yield 31.2%, 3.2× over-collection in derived JSON |

## Assignment Q3 — Evaluation

| Consideration | Assessment | V2 action |
|---------------|------------|-----------|
| Benchmark list vs hierarchy | **Weak** V1 | `eval_hierarchy.json`: capability→offline→task→human→business |
| Deployment metrics in gate | **Missing** V1 | L3 includes latency p99, hallucination rate, ₹/query |
| Task definitions | **Missing** V1 | Gov/Edu: RBI circular QA, NCERT tutoring, GST form assist |

## Assignment Q4 — Tokenizer

| Consideration | Assessment | V2 action |
|---------------|------------|-----------|
| Vocab size Pareto | **Missing** V1 | `vocab_size_tradeoff.json`: 96k–256k comparison |
| 128k justification | **Asserted** V1 | M2 matrix: 128k wins on embedding GB + fertility + stability |
| India USP | **Partial** V1 | Hinglish learned bucket 43k; code-switch exposure in derivation |

## Funding Decision

| Criterion | V1 | V2 target |
|-----------|-----|-----------|
| Original thinking | C+ | B+ (MCDA + fertility TCO + capability derivation) |
| Engineering judgement | C | B (cleaning DAG, kill criteria) |
| Internal consistency | B | A (single spine, derived numbers) |
| $100M approval | No | Conditional — pending human review of prose |
