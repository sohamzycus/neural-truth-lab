# Deployment Guide

Neural Truth Lab is a static-friendly Next.js 15 app with client-side TensorFlow.js training. Deploy to Netlify (recommended) or any Node host that supports Next.js.

## Prerequisites

- Node.js 20+
- npm 10+

## Local production build

```bash
npm ci
npm run typecheck
npm run lint
npm run build
npm run start
```

Open [http://localhost:3000](http://localhost:3000).

## Netlify

1. Connect the GitHub repo (`sohamzycus/neural-truth-lab`).
2. **Clear UI overrides** (Site configuration → Build & deploy → Build settings):
   - **Publish directory:** leave **empty** (do not set `/` or `.`) — `netlify.toml` sets `.next`
   - **Build command:** leave **empty** — uses `netlify.toml`
   - **Plugins:** remove any manually installed `@netlify/plugin-nextjs` v4 from the Netlify UI; Netlify auto-enables the v5 runtime for Next.js 15
3. Build settings from `netlify.toml`:
   - **Build command:** `npm ci && npm run build`
   - **Publish:** `.next`
   - **Node:** 20 (see `.nvmrc`)
4. Optional env var:
   - `NEXT_PUBLIC_SITE_URL` — canonical URL for Open Graph metadata (e.g. `https://your-site.netlify.app`)

After the first deploy, trigger **Clear cache and deploy site** if a prior build cached bad settings.

## GitHub Actions

CI runs on every push/PR to `main`:

- `npm run typecheck`
- `npm run lint`
- `npm run build`

See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Manual checklist before deploy

- [ ] All four labs train end-to-end in production build
- [ ] No console errors on landing and lab pages
- [ ] `prefers-reduced-motion` disables heavy animations
- [ ] Lighthouse Accessibility ≥ 90 (Chrome DevTools)

## Architecture

See [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md) and [`specs/architecture.md`](../specs/architecture.md).
