# Review 1 — Student Perspective

**Question:** Can I understand attention in 5 minutes?

## Score: 8.5 / 10

## Strengths

- Opening hook ("Who should I listen to?") immediately frames the problem, not a taxonomy
- 60-second mode provides a fast on-ramp
- Causal masking experiment teaches the concept in under 30 seconds with visual lock icons
- O(n²) slider makes the quadratic wall visceral — seeing 1M → 1T pairs lands
- KV cache simulator with MHA/GQA/MQA toggle directly answers "why does GQA exist?"
- Trade-off cards (+ buys / − gives up / → when) on every mechanism prevent oversimplification

## Issues Found & Fixed

| Issue | Resolution |
|-------|------------|
| Empty session8 had no entry point | Built full guided chapter flow |
| Chapter 10 missing content | Added hybrid-systems narrative section |
| Lint scanned node_modules | Added `.oxlintrc.json` ignore |

## Remaining Minor Gaps

- Could add more animated attention edges in opening (current step-through is functional)
- Mobile timeline horizontal scroll works but is dense on small screens

## Verdict

A motivated student can grasp the causal evolution of attention in 5 minutes via 60-second mode + opening, and deepen understanding through experiments in 20–30 minutes.
