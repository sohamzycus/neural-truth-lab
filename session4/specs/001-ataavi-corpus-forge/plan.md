# Implementation Plan — Ataavi Corpus Forge

## Tech Stack

- React 19, TypeScript, Vite 6
- Tailwind CSS 4 (`@tailwindcss/vite`)
- Framer Motion, Lucide React, Recharts
- Static JSON under `web/public/data/`
- Netlify: `npm ci && npm run build` → `dist`

## Architecture

```
session4/web/
  netlify.toml
  package.json
  index.html
  public/data/*.json
  src/
    main.tsx App.tsx index.css types.ts
    components/shell/ monitor/ ui/ charts/ sections/
    lib/scrub/
```

Single-page scroll. `AppShell` owns nav + progress. Sections import typed JSON. `HealthMonitor` jitters baseline metrics. Scrub playground uses `lib/scrub/*`.

## Data Files

dataset_stats, raw_observations, pipeline_stages, strategies, domain_enhancements, surgery_metrics, comparisons, discoveries, corpus_stats, roadmap, lessons, health_baseline, scrub_samples

## Visual

Dark tokens (`--bg` `#0a0a0b`, `--accent` `#7eb8ff`). DM Sans + JetBrains Mono. No flashy gradients.

## Testing

- `npm run typecheck`
- `npm run build`
- `src/lib/scrub/selfcheck.ts` assert-based

## Out of Scope

Auth, backend, live APIs, light theme, multi-route SPA
