# Ataavi Corpus Forge

**Jira**: N/A (course project)  
**Jira type**: N/A  
**Design**: `docs/superpowers/specs/2026-07-25-ataavi-corpus-forge-design.md`

## Summary

Production-quality React portal that engineers noisy community bird observation notes into a clean LLM pretraining corpus for Ataavi — a future multimodal Bird Foundation Model. Single continuous-scroll dark UI with sticky nav, floating Corpus Health Monitor, interactive pipeline, Session 4 strategies, domain enhancements, surgery metrics, before/after scrub playground, discoveries, charts, roadmap, and lessons.

## Clarifications

### Session 2026-07-25

- Q: Navigation model? → A: Single continuous scroll (Option A).
- Q: Geographic focus? → A: India-primary with thin global slice (Option C).
- Q: Cleaning depth? → A: Hybrid curated JSON + client scrub playground (Option C).
- Q: Architecture? → A: Section modules + shared shell (Approach 2).

## User Scenarios

### US1 — Portal shell & hero narrative (P1)

As a reviewer, I open the site and immediately understand Ataavi Corpus Forge as an internal AI tooling portal, with a clear path from observations to foundation model.

**Acceptance**
- Dark premium hero with title + subtitle
- Animated pipeline illustration (Observation → Cleaning → KG → FM → Ataavi)
- Sticky nav + reading progress
- Floating health monitor with 7 live-tweened metrics

### US2 — Dataset & raw noise (P1)

As a data engineer, I see corpus scale and why cleaning is required.

**Acceptance**
- Dataset explorer stats (counts, languages, species, years, length, observers)
- Sample observations
- Raw cards showing GPS, PII, HTML, OCR, Unicode, mixed language, repeats

### US3 — Pipeline & Session 4 strategies (P1)

As a reviewer, I can explore each cleaning stage and the 10 preprocessing strategies.

**Acceptance**
- 12 clickable pipeline nodes with purpose/technique/I/O/challenges
- 10 expandable strategy cards with why/algorithms/before/after

### US4 — Domain surgery & compare (P1)

As a domain specialist, I see bird-specific enhancements and curated + live cleaning.

**Acceptance**
- 8 domain enhancement blocks
- Surgery dashboard animated counters
- Before/after split with transform highlights
- Scrub playground runs client transforms on sample notes

### US5 — Insights, stats, roadmap, lessons (P2)

As a stakeholder, I browse discoveries, charts, multimodal roadmap, and takeaways.

**Acceptance**
- Discovery insight tiles
- Charts: language, species, quality, dedupe, readiness
- Roadmap to multimodal Ataavi
- Lessons learned section

## Requirements

- R1: React + TypeScript + Vite + Tailwind 4 + Framer Motion + Lucide + Recharts
- R2: All sample content in `web/public/data/*.json`
- R3: Responsive; Netlify-ready via `session4/web/netlify.toml`
- R4: No Lorem Ipsum; realistic bird notes
- R5: No auth/backend; static deploy
- R6: Scrub pure functions + one assert-based self-check

## Success Criteria

Reviewer thinks: “internal AI tooling dashboard.” Memorable health monitor. Complete engineering narrative.
