# Deploy Session 13 — Reversibility Lab

**Target site name:** `reversibility-lab-erav5`  
**URL (after deploy):** https://reversibility-lab-erav5.netlify.app

## Option A — Netlify Git (no API token; recommended)

1. https://app.netlify.com → **Add new site** → **Import from Git**
2. Repo: `sohamzycus/neural-truth-lab`, branch `main`
3. **Base directory:** `session13/web/interactive-lab`
4. Build settings come from `netlify.toml` (prebuilt `dist/`)
5. Deploy

## Option B — GitHub Actions

Workflow: `.github/workflows/netlify-deploy-session13.yml`

Requires a valid **`NETLIFY_AUTH_TOKEN`** in repo secrets (current secret returns **401** — regenerate at Netlify → User settings → Applications → Personal access tokens, then):

```bash
gh secret set NETLIFY_AUTH_TOKEN -R sohamzycus/neural-truth-lab
gh workflow run netlify-deploy-session13.yml -R sohamzycus/neural-truth-lab
```

## Option C — Netlify MCP (Cursor)

Netlify is in `~/.cursor/mcp.json` (`npx -y @netlify/mcp`). Run **MCP: Authenticate** for Netlify in Cursor, then ask the agent to `deploy-site` with:

`deployDirectory`: `.../session13/web/interactive-lab/dist`

## Option D — Local script

```bash
export NETLIFY_AUTH_TOKEN="..."   # fresh token
bash session13/scripts/deploy_netlify.sh
```

## Rebuild static assets

```bash
cd session13/web/interactive-lab
npm run build
git add dist && git commit -m "Rebuild lab dist" && git push
```
