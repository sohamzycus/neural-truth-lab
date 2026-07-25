# Ataavi Corpus Forge

Dark, scroll-narrative portal for engineering bird observation notes into a training corpus.

## Develop

```bash
cd session4/web
npm install
npm run dev
```

## Verify

```bash
npm run selfcheck
npm run typecheck
npm run build
```

## Deploy (Netlify)

- Base directory: `session4/web`
- Config: `netlify.toml` (`npm ci && npm run build` → `dist`)

## SpecKit

See `../specs/001-ataavi-corpus-forge/` and `../.specify/extensions/fleet/fleet-config.yml`.
