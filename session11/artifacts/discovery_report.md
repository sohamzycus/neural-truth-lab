# ERA V5 Session 11 — Repository Discovery Report

**Date:** 2026-09-13  
**Phase:** 0 (pre-implementation)  
**Status:** COMPLETE — implementation may proceed

---

## 1. Repository Map

```
erav5/
├── README.md                    # Session index (sessions 1–10 listed; 11 not yet)
├── DEPLOYMENT.md                # Netlify per-session deploy map
├── docs/                        # Cross-session design docs
├── session1/                    # Next.js Neural Truth Lab (web)
├── session2/                    # SamaBPE tokenizer (python + web)
├── session3/                    # India-40B report (web + specs/)
├── session4/                    # Ataavi Corpus Forge (web + specs/)
├── session5/                    # Mixture/curriculum plan (docs + JSON spec)
├── session6/                    # Training Data OS (fake trainer, ledger, checkpoints)
├── session7/                    # Kronecker/decoder research (numpy, YAML config)
├── session8/                    # Attention Evolution (web only)
├── session9/                    # Loss Forensics Lab (notebook, AdamW inline)
├── session10/                   # Truth Lab ★ primary reuse target
│   ├── truth_lab/               # PyTorch package: model, data, training, metrics
│   ├── scripts/                 # run_all, run_experiments, audit, generate_readme
│   ├── tests/                   # pytest evidence tests
│   └── outputs/                 # results.json, plots/
└── session11/                   # EMPTY — target for Optimizer Evidence Lab
```

---

## 2. Reusable Components

| Component | Source | Reuse Strategy |
|-----------|--------|----------------|
| **TinyGPT model** | `session10/truth_lab/model.py` | Copy to `src/core/model.py`; extend width via `n_embd` |
| **TinyCorpus + make_batch** | `session10/truth_lab/data.py` | Copy to `src/core/data.py` unchanged |
| **LabConfig + set_seed** | `session10/truth_lab/config.py` | Extend in `src/core/schemas.py` with optimizer/schedule/runtime configs |
| **Training loop** | `session10/truth_lab/training.py` | Refactor to `src/core/training.py`; add scheduler hooks, layer ratio logging |
| **StepLog / update_norm** | `session10/truth_lab/training.py` | Reuse pattern for EXP-RATIO-001 |
| **Audit pipeline** | `session10/scripts/audit_submission.py` | Adapt for Session 11 checklist |
| **run_all orchestration** | `session10/scripts/run_all.py` | Adapt with `--mode smoke/full` |
| **Evidence/ledger pattern** | `session6/project/ledger/` | Borrow append-only JSONL concept (not fake trainer) |
| **Checkpoint schema** | `session6/project/core/checkpoint_engine.py` | Reference only; Session 11 does not need resume |
| **Forensic README style** | `session9/README.md`, `session10/README.md` | CLAIM → EVIDENCE → VERDICT sections |
| **YAML config** | `session7/configs/default.yaml` | Precedent for `experiment_spec.yaml` |

### Not Reusable (must build fresh)

- Manual Adam implementation (independent of PyTorch calc)
- Adam with/without bias correction toggle
- Cosine and WSD LR schedules
- Controlled comparison validator
- Optimizer Evidence Ledger (JSONL + MD)
- Spec-driven YAML validation pipeline
- Width/LR sweep orchestration
- Decision policy engine

---

## 3. Integration Plan

### Architecture

Place Session 11 under `session11/` following session10 conventions but with spec-driven layout per assignment:

```
session11/
├── specs/                       # SPEC-DRIVEN MODE (created before code)
├── src/
│   ├── core/                    # schemas, config, model, data, training, seed, hash
│   ├── optimizers/              # adam_manual, adam_reference, bias variants
│   ├── schedules/               # cosine, wsd
│   ├── experiments/             # one module per EXP-*
│   ├── metrics/                 # ratio, convergence, smoothing
│   ├── validation/              # comparison_validator, result_validator
│   └── reporting/               # ledger, plots, tables, markdown
├── scripts/                     # validate_specs, run_*, run_all, audit
├── tests/
├── outputs/                     # evidence artifacts
├── artifacts/                   # discovery report, traceability matrix
└── README.md
```

### Reuse vs Fork Decision

**Fork session10 model/data/training** into `src/core/` rather than importing across sessions. Rationale:

1. Session 11 needs extensive training-loop modifications (schedulers, layer ratios, controlled comparisons).
2. Cross-session imports would create coupling and risk breaking session10.
3. session10's `TinyGPT` + `TinyCorpus` are ~300 lines total — minimal duplication cost.

### Session 10 Training Loop Gaps to Fill

Current `train_steps()` uses fixed AdamW with no scheduler. Session 11 adds:

- Configurable optimizer factory (Adam with bias toggle)
- Cosine and WSD schedule injection
- Per-layer update-to-weight ratio logging
- Controlled-run hashing and comparison validation
- Smoke/full execution modes

---

## 4. Proposed File Changes

| Action | Path | Traces To |
|--------|------|-----------|
| CREATE | `session11/specs/*.yaml, *.md` | All spec IDs |
| CREATE | `session11/src/**` | EXP-*, METRIC-*, CLAIM-* |
| CREATE | `session11/scripts/**` | Reproducibility commands |
| CREATE | `session11/tests/**` | Acceptance criteria |
| CREATE | `session11/outputs/**` | Generated at runtime |
| CREATE | `session11/README.md` | Generated from artifacts |
| CREATE | `session11/requirements.txt` | session10 + pyyaml |
| UPDATE | `erav5/README.md` | Add session11 entry (after completion) |

**No modifications** to sessions 1–10.

---

## 5. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Full-mode LR sweep (3 widths × grid) is slow on CPU | Medium | Smoke mode uses 3 LR points; full uses documented grid |
| MPS/CUDA nondeterminism | Medium | Force CPU in tests; document device in evidence records |
| WSD schedule definition ambiguity | Low | Define precisely in `experiment_spec.yaml` |
| README fake numbers | High | Generate README sections from `outputs/` only |
| Comparison invalid if init differs | High | `comparison_validator.py` rejects before conclusion |
| session11 empty dir | None | Expected — greenfield |

---

## 6. Unresolved Ambiguities

| Item | Resolution |
|------|------------|
| WSD formula | Define as: linear warmup → stable plateau → linear/cosine decay (documented in spec) |
| Width 4096 | NOT run in smoke or default full; extrapolation only with LOW confidence |
| Official comparison step | Step 200 per assignment; step 300 diagnostic |
| Notebook required? | Assignment emphasizes scripts + README; no notebook required (session10 had one; session11 uses spec-driven scripts) |
| `pyyaml` dependency | Add to requirements.txt for spec validation |

---

## 7. ERA V5 Conventions Observed

1. **Self-contained sessions** — each session has own venv, requirements, scripts.
2. **Evidence-first** — outputs committed or regenerated via `run_all.py`.
3. **Audit gate** — `audit_submission.py` prints PASS/FAIL checklist.
4. **Deterministic seeds** — seed 1337 default in session10.
5. **CPU-safe tests** — force CPU in pytest for reproducibility.
6. **matplotlib Agg backend** — for headless plot generation.
7. **No shared Python package** at repo root.

---

## 8. Go/No-Go

**GO** — session10 provides model/data/training foundation; session6 provides ledger pattern; no session11 conflicts exist. Proceed to Stage 2 (specifications).
