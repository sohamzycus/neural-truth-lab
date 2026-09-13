# ERA V5 Session 11 — Optimizer Evidence Lab

## Product Specification

**Product ID:** PROD-OPT-LAB-001  
**Title:** Optimizer Evidence Lab  
**Version:** 1.1

## Thesis

When we claim an optimizer or schedule is "better," we must specify what was measured, under what controls, and how much should we trust the conclusion.

## Novelty (vs a Normal Experiment Runner)

A normal experiment runner executes configs and writes metrics. **This lab adds an auditable claim lifecycle:**

| Normal runner | Optimizer Evidence Lab |
|---------------|------------------------|
| Runs experiments | Runs experiments **only after spec validation** |
| Writes metrics JSON | Writes **EvidenceRecord** linking claim → raw artifacts → derived metrics → decision → confidence |
| Implicit "A beat B" | **Comparison validator** rejects uncontrolled diffs as `INVALID_EXPERIMENT` |
| Single README prose | README **generated from artifacts**; numeric results forbidden outside artifact injection |
| One output folder | **execution_mode** homogeneity enforced; smoke/full never mixed in one report |
| Ad-hoc conclusions | **Decision policy** (DECISION-001…008) with documented thresholds |

**Novelty is not "we ran Adam experiments."** Novelty is the **Optimizer Evidence Ledger** plus **mandatory control validation** before any comparative conclusion.

## Claim Registry

Each claim maps to exactly one primary experiment and one evidence record.

| Claim ID | Statement | Experiment | Success criterion (spec) |
|----------|-----------|------------|--------------------------|
| CLAIM-001 | Manual Adam matches PyTorch to high precision | EXP-ADAM-001 | max_abs_diff ≤ 1e-6 → SUPPORTED |
| CLAIM-002 | Bias correction measurably changes early updates | EXP-BIAS-001 | step-1 abs_diff > 0 AND convergence step reported or NOT_REACHED |
| CLAIM-003 | Update-to-weight ratio shows detectable warmup transition | EXP-RATIO-001 | warmup_end_step MEASURED; stabilization reported or NOT_REACHED |
| CLAIM-004 | WSD vs cosine differs at step 200 under controls | EXP-SCHEDULE-001 | validator VALID; decision from policy, not manual winner pick |
| CLAIM-005 | Optimal stable LR depends on measured width | EXP-LR-001 | minima MEASURED at widths 256/512/1024 only |

**Forbidden:** labelling any claim `proven` or `SUPPORTED` without a matching EvidenceRecord and existing raw artifacts.

## Experiments

| ID | Title |
|----|-------|
| EXP-ADAM-001 | Reproduce Adam by hand |
| EXP-BIAS-001 | Bias correction investigation |
| EXP-RATIO-001 | Update-to-weight evidence |
| EXP-SCHEDULE-001 | Cosine vs WSD |
| EXP-LR-001 | Width / learning-rate landscape |

## Execution Modes

| Mode | Purpose | Must differ from other mode |
|------|---------|----------------------------|
| smoke | Fast pipeline validation | steps, grids, widths |
| full | Assignment configuration | steps=300 schedule, full LR grid |

Every artifact row/record **must** include `execution_mode`.  
A ledger or README **must not** combine records from different modes.

## Separation of Concerns

1. Mathematical correctness (EXP-ADAM-001)
2. Implementation correctness (manual vs PyTorch)
3. Optimization behavior (EXP-BIAS-001)
4. Schedule behavior (EXP-SCHEDULE-001)
5. Scaling behavior (EXP-LR-001)
6. Practical decision-making (decision_policy.yaml)
7. Confidence and uncertainty (evidence ledger)

## Evidence Provenance Chain (required)

```
ExperimentSpec.id
  → raw artifact file(s) on disk
    → derived metric (with label: MEASURED | CALCULATED | INFERRED | NOT_REACHED | UNAVAILABLE)
      → DecisionRecord / claim status
        → confidence (HIGH | MEDIUM | LOW | NONE)
```

No link in this chain may be skipped.
