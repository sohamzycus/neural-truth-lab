# Schedule Decision — EXP-SCHEDULE-001

**Execution mode:** smoke
**Control validation:** VALID
**Training budget:** 300 steps each run
**Official comparison checkpoint:** step 200 (index 199)

| Schedule | Loss @ step 200 | Loss @ step 300 | Best loss | Variance |
|----------|----------------:|----------------:|----------:|---------:|
| cosine | 1.7466 | 1.4769 | 0.8260 | 0.444915 |
| wsd | 1.6353 | 1.3926 | 0.7609 | 0.487326 |

**Relative diff at step 200:** 0.0681 (MEASURED)
**Decision:** SUPPORTED
**Model I would keep:** WSD (based on lower loss at step 200 under validated controls)

Step 300 reported as late-stage diagnostic only.
