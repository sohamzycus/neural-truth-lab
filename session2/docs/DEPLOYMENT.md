# Deployment — SamaBPE

Static Vite/React app. All metrics ship in `public/data/` (no Python on Netlify).

## Netlify (GitHub)

1. [app.netlify.com](https://app.netlify.com) → site **sama-bpe-tokenizer** (or import `sohamzycus/neural-truth-lab`)
2. **Site configuration → Build & deploy → Build settings**
   - **Base directory:** leave **empty** (repo-root `netlify.toml` sets `build.base = "session2/web"`)
   - **Build command / Publish directory:** leave **empty** (uses `netlify.toml`)
3. Deploy. URL: `https://sama-bpe-tokenizer.netlify.app`

If build fails with “No such file or directory” for `session2/web/scripts/...`, the UI base directory is set **and** conflicts with root `netlify.toml` — clear the UI base directory field.

## Local

```bash
cd session2/web
npm ci && npm run build
npx serve dist
```

## Session1 (Neural Truth Lab)

Existing site: [neural-truth-lab.netlify.app](https://neural-truth-lab.netlify.app)

After the monorepo move, set **Base directory** to `session1` in Netlify UI (Build & deploy).
