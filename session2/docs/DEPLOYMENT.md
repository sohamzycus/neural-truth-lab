# Deployment — SamaBPE (session2)

**Production:** https://sama-bpe-tokenizer-413.netlify.app

Netlify site on account `niyogi.soham@gmail.com` (team: Soham's Buddies). Legacy URL `sama-bpe-tokenizer.netlify.app` was on a different account.

Static Vite/React app. Metrics ship in `public/data/`; production bundle in `web/dist/` (committed for Netlify).

## Netlify (sama-bpe-tokenizer site)

### Required site settings

| Setting | Value |
|---------|--------|
| **Base directory** | `session2/web` |
| **Build command** | empty |
| **Publish directory** | empty |

Config is in `session2/web/netlify.toml` (verifies prebuilt `dist/`, no npm on Netlify).

Netlify’s build image often fails `npm install` (~8 min crash). We **commit `session2/web/dist/`**; the build step only checks it exists.

### After frontend changes

```bash
cd session2/web
npm ci && npm run build:netlify
git add dist/ public/data/ && git commit && git push
```

Then **Clear cache and deploy** on the sama-bpe Netlify site.

## Session 1 (Neural Truth Lab)

**Do not** use this site for session1. Use https://llmlab.netlify.app with base directory **`session1`**. See `session1/docs/DEPLOYMENT.md` and repo-root `DEPLOYMENT.md`.

## Local

```bash
cd session2/web
npm ci && npm run build
npx serve dist
```

## GitHub Actions

`.github/workflows/netlify-deploy.yml` can zip-deploy `dist/` when `NETLIFY_AUTH_TOKEN` + `NETLIFY_SITE_ID` (sama-bpe site) are set.
