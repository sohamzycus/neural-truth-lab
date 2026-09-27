# Deploy to Netlify

## Option A — Git-connected site (recommended)

1. [Netlify](https://app.netlify.com) → **Add new site** → **Import from Git**
2. Repository: `sohamzycus/neural-truth-lab`
3. Branch: `main`
4. **Base directory:** `session13/web/interactive-lab`
5. Build command and publish directory are read from `netlify.toml` (prebuilt `dist/`).
6. Deploy.

After changing the React app:

```bash
cd session13/web/interactive-lab
npm run build
git add dist netlify.toml
git commit -m "Rebuild Session 13 lab dist"
git push
```

## Option B — CLI one-off

```bash
cd session13/web/interactive-lab
npm run build
npx netlify-cli deploy --prod --dir=dist
```

First time: `npx netlify-cli login` and link the site.

## Verify

- `/data/results.json` loads (measured runs)
- `/data/host_profile.json` loads (laptop evidence)
