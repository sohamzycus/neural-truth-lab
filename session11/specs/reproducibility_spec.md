# Reproducibility Specification

## Environment

```bash
cd session11
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Validation Gate

```bash
python scripts/validate_specs.py
```

Must pass before any experiment runs. Validates YAML structure, claim/experiment linkage, and cross-spec consistency.

## End-to-End Single Command (required)

After implementation aligns with v1.1 specs:

```bash
# Smoke (CI / fast check)
python scripts/run_all.py --mode smoke && python scripts/generate_readme.py && python scripts/audit_submission.py

# Full (submission)
python scripts/run_all.py --mode full && python scripts/generate_readme.py && python scripts/audit_submission.py
```

`run_all.py` must: validate specs → clear ledger → run all experiments → write ledger → (caller or script) generate README.  
`audit_submission.py` is the final gate and must fail on mixed execution modes.

## Smoke Mode

```bash
python scripts/run_all.py --mode smoke
python scripts/generate_readme.py
python scripts/audit_submission.py
```

Reduced: steps, LR grid, widths. **Not valid for submission claims requiring full config.**

## Full Mode

```bash
python scripts/run_all.py --mode full
python scripts/generate_readme.py
python scripts/audit_submission.py
```

Assignment configuration: 300 schedule steps, 20 bias steps, 3 widths × 7 LR points.

## Execution Mode Separation (mandatory)

1. Every CSV row, JSON object, and EvidenceRecord includes `execution_mode`.
2. `evidence_ledger.jsonl` must contain **one mode only** per run.
3. README banner states that mode, read from ledger record 1.
4. Audit rejects ledger with mixed modes.
5. Do not append smoke records after full run without clearing ledger.

## Individual Experiments

| Experiment | Command |
|------------|---------|
| EXP-ADAM-001 | `python scripts/run_adam_verification.py` |
| EXP-BIAS-001 | `python scripts/run_bias_correction.py --mode full` |
| EXP-RATIO-001 | `python scripts/run_layer_ratios.py --mode full` |
| EXP-SCHEDULE-001 | `python scripts/run_schedule_comparison.py --mode full` |
| EXP-LR-001 | `python scripts/run_lr_sweep.py --mode full` |

## Tests

```bash
python -m pytest tests/ -q
```

See `acceptance_criteria.yaml` → `required_tests` for the full mandated list.

## Seed Policy

- Default seed: 1337
- Batch seed: `cfg.seed + seed_offset + step`
- All RNG sources seeded via `set_seed()`
- EXP-BIAS-001 gradients: fixed list (no RNG)

## Device Policy

- Tests: CPU only
- Experiments: CPU default (documented in evidence record)
- CUDA/MPS allowed but nondeterminism noted in limitations

## Git Commit

Evidence records capture `git rev-parse HEAD` when available.

## Number Labels

All reported numbers must be labelled:

| Label | Meaning |
|-------|---------|
| MEASURED | Direct from experiment output |
| CALCULATED | Deterministic transform of measured values |
| INFERRED | Extrapolation (e.g. width 4096) |
| ILLUSTRATIVE | Docs/examples only — never in results tables |
| NOT_REACHED | Threshold/window exhausted |
| UNAVAILABLE | Not computed |

**Forbidden:** ILLUSTRATIVE or hand-typed numbers in README results sections.
