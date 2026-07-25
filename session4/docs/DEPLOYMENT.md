# Ataavi Corpus Forge — Netlify Deploy

CLI file upload is blocked on corporate networks (Zscaler → `403 Forbidden`). Use **committed `dist/` + GitHub Actions** (same pattern as session2 SamaBPE and session3 India-First 40B).

## One-time Netlify setup

1. Site: **ataavi-corpus-forge** — https://ataavi-corpus-forge.netlify.app
2. Site ID: `5b66323b-3d13-4ef1-b1a8-95448d36aef2`
3. Optional: link GitHub in Netlify UI with base directory `session4/web` (workflow deploy is primary)

`session4/web/netlify.toml` verifies committed `dist/` — no `npm install` on Netlify (~seconds).

## After UI changes

```bash
cd session4/web
npm run build:netlify
git add -f dist/
git commit -m "chore(session4): rebuild dist"
git push
```

GitHub Actions (`.github/workflows/netlify-deploy-session4.yml`) deploys on push to `main`.

## Live URL

https://ataavi-corpus-forge.netlify.app
