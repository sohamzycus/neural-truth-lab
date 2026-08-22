# Session 8 — Netlify Deployment

**Site:** [attention-evolution-session8](https://app.netlify.com/projects/attention-evolution-session8)  
**URL:** https://attention-evolution-session8.netlify.app  
**Site ID:** `23eb2bfe-1bd9-4d30-ac96-57564b9dee0f` (personal account — PAT zip deploy)

## Netlify UI settings

**Site configuration → Build & deploy → Build settings**

| Setting | Value |
|---------|-------|
| Base directory | `session8/web` |
| Build command | *(empty — uses netlify.toml)* |
| Publish directory | *(empty)* |

Config file: `session8/web/netlify.toml` → `npm run build` → `dist/`

## Deploy options

### 1. GitHub Actions (recommended after push)

Workflow: `.github/workflows/netlify-deploy-session8.yml`  
Uses repo secret `NETLIFY_AUTH_TOKEN` + site ID above.

```bash
git push origin main
# or trigger manually:
gh workflow run netlify-deploy-session8.yml -R sohamzycus/neural-truth-lab
```

### 2. CLI (local)

```bash
cd session8/web
npm run build
npx netlify-cli@17 link --id 23eb2bfe-1bd9-4d30-ac96-57564b9dee0f
bash ../scripts/deploy_netlify.sh
```

### 3. Netlify UI drag-and-drop

1. `cd session8/web && npm run build`
2. Open https://app.netlify.com/projects/attention-evolution-session8/deploys
3. Drag `session8/web/dist/` onto the deploy dropzone

### 4. Netlify MCP (Cursor)

Re-authenticate **user-netlify** MCP in Cursor Settings if deploy tools time out.

## Local verify

```bash
cd session8/web
npm ci
npm run build
npm test
npm run lint
```
