# Deployment — India-First 40B (session3)

**Production:** https://india-40b-erav5.netlify.app  
**Netlify project:** https://app.netlify.com/projects/india-40b-erav5

Static Vite/React report viewer. Metrics ship in `public/data/`; production bundle in `web/dist/` (committed for Netlify).

## Netlify site settings

| Setting | Value |
|---------|--------|
| **Base directory** | `session3/web` |
| **Build command** | empty (uses `netlify.toml`) |
| **Publish directory** | empty (uses `netlify.toml`) |
| **Env vars** | None required |

Config: `session3/web/netlify.toml`

## After changes

```bash
cd session3
python3 scripts/derive_all.py
python3 scripts/export_report_data.py
cd web && npm ci && npm run build:netlify
git add dist/ public/ && git commit && git push
```

Then either:

**Option A — Git push** (after adding `NETLIFY_SITE_ID_SESSION3=f2cbbb76-00cd-4b8a-ab7b-d1861387ef06` to GitHub secrets):

```bash
git add session3/web/dist session3/web/public && git commit && git push
```

**Option B — Manual drag-drop:** Netlify → india-40b-erav5 → Deploys → drag `session3/web/dist` folder.

**Option C — Zip deploy** (if `NETLIFY_AUTH_TOKEN` is set):

```bash
cd session3/web/dist && zip -r ../deploy.zip .
curl -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
     -H "Content-Type: application/zip" \
     --data-binary @../deploy.zip \
     "https://api.netlify.com/api/v1/sites/f2cbbb76-00cd-4b8a-ab7b-d1861387ef06/deploys"
```

## Local preview

```bash
cd session3/web
npm ci && npm run build && npx serve dist
```
