# erav5

Monorepo with **two independent Netlify sites** (same GitHub repo):

| Session | App | URL | Netlify base directory |
|---------|-----|-----|------------------------|
| `session1/` | Neural Truth Lab (Next.js) | https://llmlab.netlify.app | **`session1`** |
| `session2/web/` | SamaBPE Tokenizer Lab (Vite) | https://sama-bpe-tokenizer.netlify.app | **`session2/web`** |

**Important:** There is no root `netlify.toml`. Each site must use its own base directory in the Netlify UI.

See [`DEPLOYMENT.md`](./DEPLOYMENT.md), `session1/docs/DEPLOYMENT.md`, and `session2/docs/DEPLOYMENT.md`.
