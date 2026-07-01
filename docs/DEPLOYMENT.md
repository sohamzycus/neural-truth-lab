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
2. Build settings are read from `netlify.toml`:
   - **Build command:** `npm ci && npm run build`
   - **Plugin:** `@netlify/plugin-nextjs` v5 (installed as devDependency)
   - **Node:** 20 (see `.nvmrc`)
3. Optional env var:
   - `NEXT_PUBLIC_SITE_URL` — canonical URL for Open Graph metadata (e.g. `https://your-site.netlify.app`)

Netlify auto-installs the Next.js plugin when declared in `netlify.toml`.

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
