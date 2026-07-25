# Ataavi Corpus Forge — Design Spec

**Date:** 2026-07-25  
**Location:** `session4/web`  
**Status:** Approved for implementation planning

## Goal

Build a production-quality React portal that narrates how noisy community bird observation notes are engineered into a clean pretraining corpus for Ataavi — a future multimodal Bird Foundation Model. The site must feel like an internal AI data-engineering tool (OpenAI / Anthropic / DeepMind caliber), not an assignment dashboard.

## Decisions Locked

| Decision | Choice |
|----------|--------|
| Navigation | Single continuous scroll + sticky section nav + progress bar |
| Corpus focus | India-primary with a thin global slice |
| Cleaning depth | Hybrid: curated JSON stats/story + client-side scrub playground |
| Architecture | Section modules + shared shell (Approach 2) |
| Deploy | Netlify static site from `session4/web` |

## Product Narrative

Ataavi is an AI-powered Bird Intelligence Platform. This app demonstrates the **textual knowledge corpus** engineering path before multimodal training (photos, vocalizations, spectrograms, habitat, migration, notes).

Story arc: raw observation → cleaning pipeline → domain surgery → training-ready corpus → multimodal roadmap → Ataavi AI.

## Information Architecture

### Shell

- Sticky header: `Ataavi / Corpus Forge`
- Sticky section anchor nav with active scroll-spy
- Thin reading-progress bar under header
- Floating **Corpus Health Monitor** (bottom-right; collapses to FAB on `<md`)
- No auth, no sidebar app chrome

### Sections (DOM `id`s)

1. `hero` — Large title **Ataavi Corpus Forge**; subtitle *Engineering a Production-Ready Bird Knowledge Corpus for Future Multimodal AI*; animated illustration chain: Bird Observation → Corpus Cleaning → Knowledge Graph → Foundation Model → Ataavi AI
2. `why-notes` — Why observation notes beat structured labels (NL, behavior, habitat, migration, weather, reasoning, uncertainty, timestamps, geolocation)
3. `dataset` — Dataset Explorer stats + sample observations
4. `raw` — Noisy observation cards (GPS, PII, HTML, repeats, taxonomy, Unicode, OCR, mixed language, broken formatting)
5. `pipeline` — Interactive 12-stage cleaning pipeline (clickable nodes)
6. `strategies` — 10 Session 4 preprocessing strategy cards (expandable)
7. `domain` — Domain-specific enhancements beyond Session 4
8. `surgery` — Corpus Surgery Dashboard with animated counters
9. `compare` — Before/after split view + scrub playground
10. `discoveries` — Browsable insight tiles
11. `stats` — Final corpus charts
12. `roadmap` — Multimodal integration path to Ataavi
13. `lessons` — Session 4 lessons learned

## Visual System

### Mood

Premium, minimal, Apple × OpenAI. Dark theme. Elegant typography. Whitespace. Subtle Framer Motion. No flashy gradients, no purple glow, no childish UI.

### Tokens

| Token | Value / role |
|-------|----------------|
| `--bg` | `#0a0a0b` page |
| `--surface` | `#121214` elevated panels |
| `--border` | white ~8% opacity hairlines |
| `--text` | `#e8e8ea` |
| `--muted` | `#8a8a93` |
| `--accent` | `#7eb8ff` cool blue, sparse use |
| `--warn` / `--danger` / `--ok` | health monitor semantics only |

### Typography

- UI / display: **DM Sans** (Google Fonts), tight tracking on hero title
- Mono: **JetBrains Mono** for IDs, GPS, hashes, pipeline labels
- Body measure ~65ch

### Surfaces & motion

- Flat panels, 1px borders, no multi-layer shadows
- Cards only when interaction needs a container
- Framer Motion: hero stagger, section fade-in on intersect, pipeline panel swap, surgery count-up, health metric tween
- Durations 200–400ms ease-out; no bounce

## Data Model

All sample content in JSON under `public/data/`. Components consume typed shapes from `src/types.ts`. No Lorem Ipsum. Realistic India-first bird notes with a few global samples.

| File | Contents |
|------|----------|
| `dataset_stats.json` | Observation/country/language/species/year/length/observer counts |
| `raw_observations.json` | Noisy cards with realistic defects |
| `pipeline_stages.json` | 12 stages: purpose, technique, input, output, challenges |
| `strategies.json` | 10 strategies: why, algorithms, before/after |
| `domain_enhancements.json` | Synonym, habitat, call, confidence, GPS mask, season, taxonomy, media |
| `surgery_metrics.json` | Counter targets for surgery dashboard |
| `comparisons.json` | Split-view pairs + transformation highlight list |
| `discoveries.json` | Insight tiles |
| `corpus_stats.json` | Chart series (language, species, quality, dedupe, readiness) |
| `roadmap.json` | Multimodal stack copy |
| `lessons.json` | Closing principles |
| `health_baseline.json` | Seed metrics + jitter ranges for monitor |
| `scrub_samples.json` | Playground inputs |

### Pipeline stages (fixed order)

Raw Observations → Content Extraction → Unicode Normalization → Language Detection → Quality Filtering → Exact Deduplication → Near Duplicate Detection → PII Removal → Ghost Tag Normalization → Benchmark Decontamination → Manifest Generation → Training Corpus

### Domain enhancements (fixed set)

1. Species synonym normalization → canonical taxonomy  
2. Habitat normalization  
3. Bird call transcription normalization  
4. Observer confidence scoring  
5. Sensitive GPS masking (conservation)  
6. Season enrichment (migration)  
7. Taxonomy reconciliation  
8. Broken media removal  

## Component Architecture

```
session4/web/
  netlify.toml
  package.json
  index.html
  public/data/*.json
  src/
    main.tsx
    App.tsx
    index.css
    types.ts
    components/
      shell/     AppShell, SectionNav, ProgressBar, Section
      monitor/   HealthMonitor
      ui/        StatTile, MetricCounter, ExpandableCard,
                 ObservationCard, BeforeAfter, PipelineNode, InsightTile
      charts/    ChartPanel wrappers (pie, bar, timeline, gauge)
      sections/  Hero, WhyNotes, Dataset, Raw, Pipeline, Strategies,
                 Domain, Surgery, Compare, Discoveries, Stats,
                 Roadmap, Lessons
    lib/scrub/   unicode, htmlStrip, piiStrip, whitespace, hashDedupe
```

### Key interactions

1. **Pipeline** — select node → detail panel (purpose / technique / I/O / challenges); active step highlight  
2. **Strategies** — accordion (one open); before/after mono blocks  
3. **Compare + Scrub** — curated split view with transform chips; playground runs real client transforms on `scrub_samples`  
4. **Surgery** — count-up on viewport enter  
5. **Stats** — Recharts for language pie, species bar, quality timeline, dedupe savings, readiness gauge  
6. **Discoveries** — insight grid; hover reveals significance  
7. **Health Monitor** — interval jitter within baseline ranges; soft tween; 7 metrics: Noise Score, Corpus Quality, Duplicate Ratio, Language Balance, Metadata Completeness, PII Risk, Training Readiness  

## Technical Stack

- React 19 + TypeScript + Vite 6  
- Tailwind CSS 4 (`@tailwindcss/vite`)  
- Framer Motion  
- Lucide React  
- Recharts (charts)  
- Static Netlify deploy; Node 20  

### Scripts

- `dev` — Vite  
- `build` — `vite build` (typecheck separately before ship)  
- `preview` — Vite preview  
- `typecheck` — `tsc --noEmit`  

### Netlify

- Config: `session4/web/netlify.toml`  
- Build: `npm ci && npm run build`  
- Publish: `dist`  
- SPA redirect `/*` → `/index.html`  
- Update root `DEPLOYMENT.md` with Session 4 row  

## Scrub Playground (client)

Pure functions only; no network. Applied to `scrub_samples.json`:

- Unicode NFKC normalization  
- HTML tag strip  
- Email / phone-like PII strip  
- Whitespace collapse  
- Optional exact-hash duplicate flag for demo pairs  

Dashboard surgery/stats remain curated JSON (not derived from running the full corpus in-browser).

## Error Handling & Resilience

- Missing JSON: section shows quiet empty state, not a white screen  
- Scrub errors: show message in playground panel; leave curated compare intact  
- Prefer graceful degradation over crash  

## Testing / Verification

- `npm run typecheck`  
- `npm run build` must produce `dist/index.html` and copy `public/data`  
- Manual smoke: scroll-spy, pipeline click, strategy expand, scrub run, health monitor updates, responsive collapse  
- One small self-check for scrub pure functions (assert-based or tiny test file; no heavy framework)

## Out of Scope

- Authentication  
- Backend / live eBird API  
- Real full-corpus processing in browser  
- Storybook  
- Light theme toggle  
- Multi-route SPA  

## Success Criteria

Reviewer reaction: “this looks like an internal AI tooling dashboard.”  
Memorable floating health monitor.  
Complete engineering narrative from noisy notes → training corpus → Ataavi multimodal path.  
Realistic bird data; Netlify-ready; responsive; dark premium aesthetic without flashy gradients.
