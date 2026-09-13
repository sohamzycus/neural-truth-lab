# LR Sweep Decision — EXP-LR-001
**Execution mode:** smoke

## Measured minima (loss vs learning rate)

| Width | Best LR | Smoothed loss at min | Label |
|------:|--------:|---------------------:|-------|
| 256 | 7.2084e-04 | 0.9695 | MEASURED |
| 512 | 7.2084e-04 | 0.9103 | MEASURED |
| 1024 | 7.2084e-04 | 0.8987 | MEASURED |

## Width 4096 (NOT MEASURED — INFERRED only)

- **Proposed LR:** 7.2084e-04 (INFERRED)
- **Confidence:** LOW — width 4096 was not run
- **Method:** log-log linear fit on measured minima
- **Scaling:** MONOTONIC
- **Why confidence is limited:** Width 4096 not measured; tiny corpus; single seed; CPU only