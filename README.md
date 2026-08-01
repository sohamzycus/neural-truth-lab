# erav5

Monorepo with **independent Netlify sites** (same GitHub repo):

| Session | App | URL | Base directory |
|---------|-----|-----|----------------|
| `session1/` | Neural Truth Lab (Next.js) | https://llmlab.netlify.app | **`session1`** |
| `session2/web/` | SamaBPE Tokenizer Lab (Vite) | https://sama-bpe-tokenizer.netlify.app | **`session2/web`** |
| `session3/web/` | India-First 40B Report | https://india-40b-erav5.netlify.app | **`session3/web`** |
| `session4/web/` | Ataavi Corpus Forge | https://ataavi-corpus-forge.netlify.app | **`session4/web`** |
| **`session5/`** | **Mixture & Curriculum Plan (Session 5 assignment)** | — | **docs only** → [`session5/README.md`](session5/README.md) |

**Session 5 submission:** open [`session5/README.md`](session5/README.md) and run `cd session5 && python3 scripts/run_all.py`.

**Important:** There is no root `netlify.toml`. Each site must use its own base directory in the Netlify UI.

See [`DEPLOYMENT.md`](./DEPLOYMENT.md).
