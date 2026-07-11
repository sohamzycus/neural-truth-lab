# Deployment — SamaBPE

Static Vite/React app. Metrics ship in `public/data/` and the production bundle in `web/dist/` (committed for Netlify).

## Netlify (GitHub)

Netlify’s build image has repeated `npm install` failures (~8 min, then crash). We **commit prebuilt `session2/web/dist/`** and Netlify only publishes it (~seconds, no npm).

1. After frontend changes: `cd session2/web && npm run build:netlify`
2. Commit `dist/` with your changes and push.
3. [sama-bpe-tokenizer](https://app.netlify.com/projects/sama-bpe-tokenizer) — base directory **empty**, build/publish **empty** (uses `netlify.toml`).

URL: `https://sama-bpe-tokenizer.netlify.app`

## Local

```bash
cd session2/web
npm ci && npm run build
npx serve dist
```

## Session1 (Neural Truth Lab)

Existing site: [neural-truth-lab.netlify.app](https://neural-truth-lab.netlify.app)

After the monorepo move, set **Base directory** to `session1` in Netlify UI (Build & deploy).
