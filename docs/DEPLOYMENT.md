# Deployment Guide

Neural Truth Lab is a **static Next.js export** — TensorFlow.js runs entirely in the browser. Deploy to any static host; Netlify is the default.

## Prerequisites

- Node.js 20+ (see `.nvmrc`)
- npm 10+

## Local production build

```bash
npm ci
npm run typecheck
npm run lint
npm run build
npx serve out
```

Open [http://localhost:3000](http://localhost:3000) (or the port `serve` prints).

## Netlify (recommended)

### One-time site setup

1. [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git** → `sohamzycus/neural-truth-lab`
2. **Site configuration → Build & deploy → Build settings**
   - **Build command:** leave **empty**
   - **Publish directory:** leave **empty**
   - (Both are read from `netlify.toml`; UI values like `/` or `.` will break deploys.)
3. **Site configuration → Environment variables** (optional):
   - `NEXT_PUBLIC_SITE_URL` = `https://your-site.netlify.app`
4. Deploy. After the first success, set the env var if needed and redeploy once.

### What `netlify.toml` does

| Setting | Value |
|---------|--------|
| Build command | `npm run netlify` (installs deps, then static export) |
| Publish directory | `out` |
| Node | 20 |

Netlify runs `npm run netlify`, which runs `npm install` then exports to `out/`. Netlify’s automatic install step is unreliable on this project, so install is bundled into the build script.

### If a deploy fails

1. **Deploys → Trigger deploy → Clear cache and deploy site**
2. Confirm UI build settings are empty (see above)
3. Check the log for `npm install` completing before `next build`

## GitHub Actions

CI on every push/PR to `main`: typecheck, lint, build. See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Manual checklist

- [ ] All four labs train end-to-end on the deployed URL
- [ ] No console errors on landing and lab pages
- [ ] Lighthouse Accessibility ≥ 90

## Architecture

See [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md).
