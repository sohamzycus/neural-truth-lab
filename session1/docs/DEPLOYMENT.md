# Deployment Guide — Neural Truth Lab (session1)

**Production:** https://llmlab.netlify.app

Static Next.js export — TensorFlow.js runs entirely in the browser.

## Netlify (llmlab site)

### Required site settings

Same repo as session2, **different base directory**:

| Setting | Value |
|---------|--------|
| **Base directory** | `session1` |
| **Build command** | empty |
| **Publish directory** | empty |

Config is in `session1/netlify.toml` (`bash scripts/netlify-build.sh` → `out/`).

Optional env: `NEXT_PUBLIC_SITE_URL=https://llmlab.netlify.app`

### If llmlab shows SamaBPE instead

The Netlify site base directory is wrong (likely repo root or `session2/web`). Set it to **`session1`**, clear cache, redeploy.

## Local production build

```bash
cd session1
yarn install   # or npm ci
npm run typecheck && npm run lint && npm run build
npx serve out
```

## Registry note

`.npmrc` / `.yarnrc` pin `registry.npmjs.org` so Netlify can install (corporate Nexus URLs in lockfiles break CI).

## GitHub Actions

Root workflow `.github/workflows/ci.yml` builds session1 on push/PR.

## Manual checklist

- [ ] Landing + all four labs train on https://llmlab.netlify.app
- [ ] No console errors
- [ ] Lighthouse Accessibility ≥ 90
