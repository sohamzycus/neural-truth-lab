# Tasks — Ataavi Corpus Forge

**Feature dir:** `session4/specs/001-ataavi-corpus-forge`  
**App root:** `session4/web`

## Phase 1: Setup

<!-- sequential -->
- [x] T001 Scaffold Vite React-TS app in `session4/web` with Tailwind 4, Framer Motion, Lucide, Recharts
- [x] T002 Add `session4/web/netlify.toml`, fonts in `index.html`, dark tokens in `src/index.css`
- [x] T003 Create `src/types.ts` matching all JSON shapes
- [x] T004 Update root `DEPLOYMENT.md` with Session 4 row

## Phase 2: Foundational data & scrub

<!-- parallel-group: 1 (max 3 concurrent) -->
- [x] T005 [P] Write `public/data/dataset_stats.json` + `raw_observations.json` + `scrub_samples.json`
- [x] T006 [P] Write `public/data/pipeline_stages.json` + `strategies.json` + `domain_enhancements.json`
- [x] T007 [P] Write `public/data/surgery_metrics.json` + `comparisons.json` + `discoveries.json`

<!-- parallel-group: 2 (max 3 concurrent) -->
- [x] T008 [P] Write `public/data/corpus_stats.json` + `roadmap.json` + `lessons.json` + `health_baseline.json`
- [x] T009 [P] Implement `src/lib/scrub/` (unicode, htmlStrip, piiStrip, whitespace, hashDedupe) + `selfcheck.ts`
- [x] T010 [P] Create UI atoms in `src/components/ui/` (StatTile, MetricCounter, ExpandableCard, ObservationCard, BeforeAfter, PipelineNode, InsightTile)

## Phase 3: US1 — Shell & hero

<!-- sequential -->
- [x] T011 [US1] Build `AppShell`, `SectionNav`, `ProgressBar`, `Section` in `src/components/shell/`
- [x] T012 [US1] Build `HealthMonitor` in `src/components/monitor/HealthMonitor.tsx`
- [x] T013 [US1] Build `HeroSection` with animated pipeline illustration

## Phase 4: US2 — Dataset & raw

<!-- parallel-group: 3 (max 3 concurrent) -->
- [x] T014 [P] [US2] Build `WhyNotesSection` in `src/components/sections/WhyNotesSection.tsx`
- [x] T015 [P] [US2] Build `DatasetSection` in `src/components/sections/DatasetSection.tsx`
- [x] T016 [P] [US2] Build `RawSection` in `src/components/sections/RawSection.tsx`

## Phase 5: US3 — Pipeline & strategies

<!-- parallel-group: 4 (max 3 concurrent) -->
- [x] T017 [P] [US3] Build `PipelineSection` with clickable nodes + detail panel
- [x] T018 [P] [US3] Build `StrategiesSection` accordion (10 cards)

## Phase 6: US4 — Domain, surgery, compare

<!-- parallel-group: 5 (max 3 concurrent) -->
- [x] T019 [P] [US4] Build `DomainSection` for 8 enhancements
- [x] T020 [P] [US4] Build `SurgerySection` with animated counters
- [x] T021 [P] [US4] Build `CompareSection` (split view + scrub playground)

## Phase 7: US5 — Discoveries, stats, roadmap, lessons

<!-- parallel-group: 6 (max 3 concurrent) -->
- [x] T022 [P] [US5] Build `DiscoveriesSection` + chart helpers in `src/components/charts/`
- [x] T023 [P] [US5] Build `StatsSection` with Recharts (pie/bar/timeline/gauge)
- [x] T024 [P] [US5] Build `RoadmapSection` + `LessonsSection`

## Phase 8: Wire & polish

<!-- sequential -->
- [x] T025 Compose all sections in `src/App.tsx` with scroll-spy ids
- [x] T026 Run scrub selfcheck, `npm run typecheck`, `npm run build`; fix issues
- [x] T027 Write `session4/README.md` with run/deploy instructions

## Dependencies

Setup → Foundational → US1 → US2/US3/US4 (after shell) → US5 → Polish  
MVP: Phase 1–5 (shell through strategies)

## Parallel notes

Fleet may fan out up to 3 `[P]` tasks per parallel-group during implement.
