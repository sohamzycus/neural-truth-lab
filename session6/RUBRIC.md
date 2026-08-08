# Session 6 — Evaluation Rubric Coverage (1,000 points)

This document maps each scoring area to **reproducible evidence** produced by:

```bash
cd session6/project
python3 run_demo.py
```

Evaluator workflow:

| Step | Action | Artifact |
|------|--------|----------|
| 1. Execute | Run `python3 run_demo.py` | Regenerates `submission_artifacts/` |
| 2. Verify | Cross-check evidence vs ledgers/manifests | `evidence.json`, `evidence.md`, `run.log` |
| 3. Inspect | Read implementation | `core/`, `ledger/`, `tests/` |

## Rubric Mapping

| Area | Points | Evidence | How to verify |
|------|--------|----------|---------------|
| **End-to-end execution** | 150 | `run.log`, full `submission_artifacts/` | `python3 run_demo.py` exits 0; all phases PASS |
| **Shards, manifests, tokenizer** | 100 | `manifests/primary_manifest.json`, `evidence.provenance` hashes | Tokenizer frozen + hash verified; manifest_hash in evidence |
| **Packing, masks, batches** | 150 | `packing` in evidence, `performance.json` verification | `metrics_verification.all_match` recomputes from batch registry |
| **Mixture, floors, OPUS** | 150 | `provenance.why_consumed.mixture`, `opus` decisions | Planned vs actual mixture; every shard scored with reason |
| **Consumption & learning ledgers** | 150 | `ledgers/*.jsonl`, `provenance.what_consumed/what_learned` | Append-only JSONL; ledger hashes in evidence |
| **Checkpoint, crash, resume, replay, fork** | 150 | `checkpoints/`, `replay`, `consumption_integrity` | No skip/duplicate batches; replay hash match; fork_meta |
| **Eval firewall** | 50 | `eval_shard_blocked` in run.log | Eval shards blocked; trainer raises on violation |
| **Throughput & packing efficiency** | 50 | `performance.json` + `metrics_verification` | Numbers derived from batches, not hardcoded |
| **Tests, evidence, docs** | 50 | `tests/`, `README.md`, `evidence.md` | `python3 -m unittest discover -s tests -v` |

## Four Proof Questions

| Question | Answer location |
|----------|-----------------|
| **What did it consume?** | `evidence.provenance.what_consumed` + `ledgers/consumption.jsonl` |
| **Why did it consume it?** | `evidence.provenance.why_consumed` (mixture + OPUS decisions) |
| **What did the model learn?** | `evidence.provenance.what_learned` + `ledgers/learning.jsonl` |
| **How can the run be reconstructed?** | `evidence.provenance.how_to_reconstruct` + replay engine |

## Automated Checks in `evidence.json`

- `consumption_integrity.no_duplicate_global_batches` — resume did not repeat batches
- `consumption_integrity.no_missing_global_batches` — resume did not skip batches
- `metrics_verification.all_match` — packing/throughput reconstructable from batches
- `replay.all_matched` — replay recomputed identical batch hashes
- `audit.all_passed` — all subsystem checks passed

## Tests

```bash
cd session6/project
python3 -m unittest discover -s tests -v
```

Key test files:

- `test_system.py` — unit tests per subsystem
- `test_rubric.py` — end-to-end submission + evidence structure

## Submission Links

| Artifact | Path |
|----------|------|
| Repository | `session6/` |
| run.log | `session6/submission/run.log` |
| evidence.json | `session6/submission/evidence.json` |
| evidence.md | `session6/submission/evidence.md` |

> `session6/submission/` is auto-synced at the end of every `run_demo.py` run.
