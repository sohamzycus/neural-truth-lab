# Traceability Matrix — Session 11 Optimizer Evidence Lab

Updated after full-mode execution on 2026-09-13.

| Spec ID | Requirement | Implementation | Test | Output Artifact | README Section | Status |
|---------|-------------|----------------|------|-----------------|----------------|--------|
| EXP-ADAM-001 | Manual Adam matches PyTorch | `src/optimizers/adam_manual.py`, `src/experiments/adam_verification.py` | `test_manual_vs_pytorch` | `outputs/adam_manual_vs_pytorch.csv` | EXP-ADAM-001 | PASS |
| EXP-BIAS-001 | Bias correction convergence | `src/experiments/bias_correction.py` | `test_bias_correction_*`, `test_convergence_detection` | `outputs/bias_correction.json` | EXP-BIAS-001 | PASS |
| EXP-RATIO-001 | Layer update ratios | `src/experiments/layer_ratios.py`, `src/metrics/ratio_metrics.py` | `test_update_to_weight_ratio` | `outputs/layer_update_ratio.csv` | EXP-RATIO-001 | PASS |
| EXP-SCHEDULE-001 | Cosine vs WSD | `src/experiments/schedule_comparison.py`, `src/schedules/` | `test_cosine_schedule`, `test_wsd_schedule` | `outputs/schedule_comparison.csv` | EXP-SCHEDULE-001 | PASS |
| EXP-LR-001 | LR width sweep | `src/experiments/lr_sweep.py` | `test_smoothed_tail` | `outputs/lr_sweep.csv` | EXP-LR-001 | PASS |
| METRIC-RATIO-001 | update/weight ratio formula | `src/metrics/ratio_metrics.py` | `test_update_to_weight_ratio` | — | Update-to-weight ratio | PASS |
| METRIC-CONVERGENCE-001 | Convergence detection | `src/metrics/convergence.py` | `test_convergence_detection` | — | Bias correction | PASS |
| CLAIM-001 | Manual Adam correct | `src/experiments/adam_verification.py` | `test_manual_vs_pytorch` | `outputs/evidence_ledger.jsonl` | Evidence Ledger | PASS |
| CLAIM-002 | Bias correction matters early | `src/experiments/bias_correction.py` | `test_bias_correction_enabled_differs_early` | evidence ledger | EXP-BIAS-001 | PASS (NOT_REACHED convergence) |
| CLAIM-003 | Ratio warmup transition | `src/experiments/layer_ratios.py` | `test_warmup_end_detection` | `outputs/layer_ratio_summary.md` | EXP-RATIO-001 | PASS |
| CLAIM-004 | Schedule comparison | `src/experiments/schedule_comparison.py` | `test_valid_controlled_comparison` | `outputs/schedule_decision.md` | EXP-SCHEDULE-001 | PASS |
| CLAIM-005 | LR scales with width | `src/experiments/lr_sweep.py` | — | `outputs/lr_sweep_decision.md` | EXP-LR-001 | PASS |
| DECISION-001 | Invalid controls → INVALID | `src/validation/comparison_validator.py` | `test_invalid_uncontrolled_comparison` | — | Claim status policy | PASS |
| DECISION-006 | Adam agree → SUPPORTED | `src/reporting/ledger.py` | `test_decision_supported_adam` | — | Confidence policy | PASS |
