# Review Fix Diff — Changes Applied

**Cycle:** 1 (Review → Fix → Re-review)  
**Build:** `npm run build` executed; `dist/` updated  
**Commit:** Not committed (per instructions)

---

## Summary

| Metric | Value |
|---|---|
| Files changed | 18 |
| New files | 2 (`PipelineSection.tsx`, review deliverables) |
| Critical fixes | 2 |
| High fixes | 4 |
| Build status | ✅ pass |
| Selfcheck | ✅ pass |

---

## Changes by area

### Assignment compliance

#### 1. Restored cleaning pipeline UI
- **Files:** `src/components/sections/PipelineSection.tsx` (new), `src/App.tsx`, `src/components/shell/AppShell.tsx`
- **Why:** `pipeline_stages.json` (12 stages) was never loaded; rubric requires pipeline narrative.
- **Impact:** Reviewers can click each stage and see purpose, technique, I/O, challenges.

#### 2. Dataset “why chosen” narrative
- **Files:** `public/data/dataset_stats.json`, `src/types.ts`, `src/components/sections/DatasetSection.tsx`
- **Why:** Assignment requires explicit dataset rationale.
- **Impact:** “Why this dataset” paragraph renders above stats grid.

#### 3. Dynamic strategy/domain counts
- **Files:** `StrategiesSection.tsx`, `DomainSection.tsx`
- **Why:** Avoid stale hardcoded “Ten” if JSON changes.
- **Impact:** Subtitles show `${strategies.length}` and `${items.length}`.

---

### Accessibility & UX

#### 4. Mobile navigation
- **Files:** `src/components/shell/AppShell.tsx`
- **Why:** Nav was `hidden` below `lg` — mobile users had no section jumps.
- **Impact:** Hamburger menu, `aria-expanded`, `aria-current`, skip-to-main link.

#### 5. Discovery tiles always show “why”
- **Files:** `src/components/ui/index.tsx`, `DiscoveriesSection.tsx`
- **Why:** Hover-only content excluded keyboard/touch users.
- **Impact:** “Why it matters” always visible; subtitle uses data-driven corpus scale.

#### 6. ARIA improvements
- **Files:** `ui/index.tsx` (`ExpandableCard`, `PipelineNode`), `RawSection.tsx`
- **Why:** Accordions and pipeline nodes lacked state semantics; search unlabeled.
- **Impact:** `aria-expanded`, `aria-controls`, `aria-pressed`, `aria-label`.

#### 7. Reduced motion support
- **Files:** `src/index.css`
- **Why:** Animations (ticker, float-bird, shimmer) had no `prefers-reduced-motion` guard.
- **Impact:** Respects OS accessibility setting.

---

### Performance & data engineering

#### 8. Health monitor lightweight sync
- **Files:** `src/lib/corpusHealth.ts`, `src/components/monitor/HealthMonitor.tsx`, `public/data/dataset_manifest.json`, `src/lib/corpusHealth.selfcheck.ts`
- **Why:** Monitor re-downloaded 1.7MB `raw_observations.json` every interval.
- **Impact:** Sync fetches surgery/stats/dataset/manifest only (~few KB). Added `shardMetaTaggedPct: 0.94` to manifest.

---

### Production / SEO

#### 9. Open Graph + Twitter meta
- **Files:** `index.html`
- **Why:** Production rubric checks OG tags.
- **Impact:** `og:title`, `og:description`, `og:type`, `og:url`, `twitter:card`.

---

### Build artifacts

#### 10. Rebuilt `dist/`
- **Files:** `dist/index.html`, `dist/assets/*`, `dist/data/*`
- **Why:** Netlify deploys prebuilt dist per `netlify.toml`.
- **Impact:** Production bundle includes pipeline section, updated JSON, new CSS/JS hashes.

---

## File change list

| File | Change |
|---|---|
| `web/src/components/sections/PipelineSection.tsx` | Added |
| `web/src/App.tsx` | Load pipeline JSON; render section; pass observationCount |
| `web/src/components/shell/AppShell.tsx` | Pipeline nav item; mobile menu; skip link |
| `web/public/data/dataset_stats.json` | Added `whyChosen` |
| `web/public/data/dataset_manifest.json` | Added `shardMetaTaggedPct` |
| `web/src/types.ts` | Optional `whyChosen` on `DatasetStats` |
| `web/src/components/sections/DatasetSection.tsx` | Render whyChosen |
| `web/src/components/sections/DiscoveriesSection.tsx` | Dynamic scale subtitle |
| `web/src/components/sections/StrategiesSection.tsx` | Dynamic count subtitle |
| `web/src/components/sections/DomainSection.tsx` | Dynamic count subtitle |
| `web/src/components/sections/RawSection.tsx` | Search `aria-label` |
| `web/src/components/ui/index.tsx` | ARIA + InsightTile fix |
| `web/src/lib/corpusHealth.ts` | Object param; manifest-based metadata |
| `web/src/lib/corpusHealth.selfcheck.ts` | Updated call signature |
| `web/src/components/monitor/HealthMonitor.tsx` | Manifest sync |
| `web/index.html` | OG/Twitter meta |
| `web/src/index.css` | `sr-only`, `prefers-reduced-motion` |
| `web/dist/**` | Rebuilt |

---

## Not changed (intentional)

- **PipelineSection prior removal:** Re-added minimally for assignment compliance; user may prefer condensed hero-only pipeline — current version is data-driven and low-line-count.
- **No git commit:** Per review instructions.
- **Bundle splitting:** Deferred (Medium finding).
- **og:image asset:** Deferred (Medium finding).
