# Ataavi Corpus Forge — Review Scorecard

**Review date:** 2026-07-25  
**Post-fix assessment** (Critical=0, High=0)

Scores use a 0–100 scale. Justification cites observable evidence only.

| Category | Score | Justification |
|---|---:|---|
| **Assignment** | 94 | All 10 required narrative elements present after pipeline + `whyChosen` fixes. Strategies (10), pipeline (12), domain extras (8), stats, lessons explicitly surfaced. Minor gap: no standalone written “lessons learned” prose outside JSON-driven section. |
| **Engineering** | 88 | Credible pipeline ordering, PII/dedupe/lang/decontam coverage, manifest-backed scale claims, scrub self-check. Corpus metrics are curated demo data, not live ETL — appropriately labeled. Health monitor now syncs lightweight manifests. |
| **Architecture** | 90 | Clean section-module layout, typed JSON bundle, shared UI primitives, single `App.tsx` composer. No backend complexity. Slight deduction: monolithic bundle, no code-splitting. |
| **UX** | 91 | Strong dark visual system, scroll narrative, animated counters, raw viewer with search/filter/download. Mobile nav fixed. Health monitor is distinctive. Dense nav list on mobile is usable but crowded. |
| **Storytelling** | 93 | Cohesive “internal tooling portal” arc from noisy notes → corpus → Ataavi FM. Hero engineering path + roadmap connect product vision. |
| **Innovation** | 85 | Live scrub playground and manifest-derived health monitor are standouts. Otherwise follows established dashboard patterns — appropriate for assignment. |
| **Maintainability** | 89 | Content in `public/data/*.json`, types aligned, self-check scripts, prebuilt dist deploy pattern documented. Generator script `scripts/generate-corpus-shard.mjs` exists for shard regen. |
| **Production Readiness** | 87 | Netlify + GHA deploy wired, SPA redirects, favicon, meta/OG tags, error states. Missing `og:image`. Prebuilt-dist pattern trades CI build simplicity for manual rebuild step. |
| **Accessibility** | 86 | Skip link, mobile menu, ARIA on expandable cards, labeled search, reduced-motion CSS, visible discovery context. Remaining: compare tabs, health panel overlap on small screens. |
| **Overall** | **89** | Production-quality demo portal that satisfies the Session 4 assignment rubric. Synthetic corpus at 47.2M is internally consistent and clearly framed as engineering narrative. |

## Score distribution

```
Assignment          █████████████████████████░░  94
Engineering         ████████████████████████░░░  88
Architecture        █████████████████████████░░  90
UX                  █████████████████████████░░  91
Storytelling        █████████████████████████░░  93
Innovation          ███████████████████████░░░░  85
Maintainability     █████████████████████████░░  89
Production          ████████████████████████░░░  87
Accessibility       ████████████████████████░░░  86
─────────────────────────────────────────────────
Overall             █████████████████████████░░  89
```

## Blocking thresholds

| Severity | Count | Blocks submission? |
|---|---:|---|
| Critical | 0 | No |
| High | 0 | No |
| Medium | 3 | No |
| Low | 3 | No |
