# India-First 40B — Netlify Deploy

CLI file upload is blocked on corporate networks (Zscaler → `403 Forbidden`). Use **Git-connected Netlify builds** (same pattern as session2 SamaBPE).

## One-time Netlify setup

1. Open [Netlify → Add new site → Import an existing project](https://app.netlify.com/start)
2. Connect **GitHub** → `sohamzycus/neural-truth-lab`
3. Site name: `india-40b-erav5` (or link existing site `f2cbbb76-00cd-4b8a-ab7b-d1861387ef06`)
4. **Build settings:**
   - **Base directory:** `session3/web`
   - **Build command:** leave **empty** (uses `netlify.toml`)
   - **Publish directory:** leave **empty**
5. Deploy

`session3/web/netlify.toml` verifies committed `dist/` — no `npm install` on Netlify (~seconds).

## After UI changes

```bash
cd session3
python3 scripts/export_report_data.py   # refresh JSON + report
cd web && npm run build
git add dist/ && git commit -m "chore(session3): rebuild dist" && git push
```

Netlify auto-deploys on push to `main`.

## Live URL

https://india-40b-erav5.netlify.app

## Site ID

`f2cbbb76-00cd-4b8a-ab7b-d1861387ef06`
