# Deployment — SamaBPE

Static Vite/React app. All metrics ship in `public/data/` (no Python on Netlify).

## Netlify (GitHub)

1. [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git** → `sohamzycus/neural-truth-lab`
2. **Site configuration → Build & deploy → Build settings**
   - **Base directory:** `session2/web`
   - **Build command:** leave **empty** (uses `netlify.toml`)
   - **Publish directory:** leave **empty**
3. Deploy. Suggested site name: `samabpe` → `https://samabpe.netlify.app`

## Local

```bash
cd session2/web
npm ci && npm run build
npx serve dist
```

## Session1 (Neural Truth Lab)

Existing site: [neural-truth-lab.netlify.app](https://neural-truth-lab.netlify.app)

After the monorepo move, set **Base directory** to `session1` in Netlify UI (Build & deploy).
