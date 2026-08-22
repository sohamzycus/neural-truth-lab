# Session 8 — Netlify Deployment

**Site:** [attention-evolution-erav5](https://app.netlify.com/projects/attention-evolution-erav5)  
**URL:** https://attention-evolution-erav5.netlify.app  
**Site ID:** `15eab089-7b3f-4d94-87bc-14d18bdbbb5f`

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
npx netlify-cli@17 link --id 15eab089-7b3f-4d94-87bc-14d18bdbbb5f
bash ../scripts/deploy_netlify.sh
```

### 3. Netlify UI drag-and-drop

1. `cd session8/web && npm run build`
2. Open https://app.netlify.com/projects/attention-evolution-erav5/deploys
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
