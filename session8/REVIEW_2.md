# Review 2 — ML Researcher Perspective

**Questions:** Are mechanisms technically correct? Are dates defensible? Are trade-offs honest?

## Score: 9 / 10

## Technical Accuracy

| Claim | Verdict |
|-------|---------|
| FlashAttention is NOT O(n) | Correct — labeled as IO improvement, same Big-O |
| GQA "not always better" than MHA | Correct — trade-off cards state diversity vs cache |
| RoPE doesn't solve long context alone | Correct — PI/NTK/YaRN section follows |
| Linear attention ≠ softmax replacement | Correct — explicit "what we lost" section |
| NTK-aware scaling = COMMUNITY ORIGIN | Correct — badge and source type set |
| MQA/GQA KV head sharing math | Correct — cache scales with kv_heads |

## Chronology Audit

- 27 mechanisms with arXiv/venue primary links
- Dates use first public arXiv submission where applicable
- DeltaNet linked to arXiv:2406.06484 (2024)
- Linear attention linked to arXiv:2006.16236 (2020)
- DeepSeek-V3 as TECHNICAL REPORT (Dec 2024)

## Issues Found & Fixed

| Issue | Resolution |
|-------|------------|
| Linear attention date typo (Jan vs Jun 2020) | Fixed to 2020-06-29 |
| Test imported .ts from node --test | Rewrote test as standalone .mjs |

## Remaining Notes

- Top-k attention date uses routing paper line; field has multiple "top-k" variants — entry notes this
- DroPE (2025) correctly marked experimental, not best practice

## Verdict

Technically credible for an educational artifact. Trade-offs are honest. No marketing claims detected.
