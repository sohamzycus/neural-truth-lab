# erav5 — monorepo deploy map

Separate **Netlify sites**, same GitHub repo (`sohamzycus/neural-truth-lab`).

| Site | URL | Netlify base directory | Config file |
|------|-----|------------------------|-------------|
| Session 1 — Neural Truth Lab | https://llmlab.netlify.app | **`session1`** | `session1/netlify.toml` |
| Session 2 — SamaBPE | https://sama-bpe-tokenizer.netlify.app | **`session2/web`** | `session2/web/netlify.toml` |
| Session 4 — Ataavi Corpus Forge | https://ataavi-corpus-forge.netlify.app | **`session4/web`** | `session4/web/netlify.toml` |

**There is no repo-root `netlify.toml`.** A root file with `base = "session2/web"` caused llmlab to publish session2 — do not add one back.

## Netlify UI (each site)

**Site configuration → Build & deploy → Build settings**

- **Base directory:** set per table above (required)
- **Build command:** leave **empty** (read from each folder’s `netlify.toml`)
- **Publish directory:** leave **empty**

After changing base directory: **Deploys → Clear cache and deploy site**.

## Local verify

```bash
# Session 1
cd session1 && yarn install && npm run build

# Session 2
cd session2/web && npm ci && npm run build:netlify

# Session 4
cd session4/web && npm ci && npm run build
```

See `session1/docs/DEPLOYMENT.md` and `session2/docs/DEPLOYMENT.md`.
