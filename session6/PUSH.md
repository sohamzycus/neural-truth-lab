# Pushing Session 6 — Troubleshooting

If `git push origin main` fails, use these methods in order.

## Quick fix (recommended)

From repo root:

```bash
bash scripts/push.sh
```

This tries SSH over port 443 first, then HTTPS via `gh`, then creates an offline `neural-truth-lab.bundle`.

## Method 1 — SSH over port 443

Port 22 is often blocked on corporate networks. GitHub provides SSH on **443**:

```bash
GIT_SSH_COMMAND='ssh -p 443 -o Hostname=ssh.github.com -o StrictHostKeyChecking=accept-new' \
  git push origin main
```

Persistent (repo-local only, does not change global git config):

```bash
cat > .git/ssh_config_github <<'EOF'
Host github.com
  Hostname ssh.github.com
  Port 443
  User git
EOF

GIT_SSH_COMMAND='ssh -F .git/ssh_config_github' git push origin main
```

## Method 2 — HTTPS via GitHub CLI

```bash
gh auth login          # if not already logged in
gh auth refresh -s repo
git -c credential.helper='!gh auth git-credential' \
  push https://github.com/sohamzycus/neural-truth-lab.git main
```

## Method 3 — HTTP 403 after upload

If you see `Writing objects: 100%` then `HTTP 403`:

1. **Secret scanning** may be blocking the push. Check email/notifications from GitHub or visit:
   - Repository → Settings → Code security → Secret scanning
2. **Re-auth** with repo scope:
   ```bash
   gh auth refresh -h github.com -s repo
   ```
3. **Smaller commit** — runtime demo outputs should not be committed. They are gitignored under `session6/.gitignore`. Regenerate locally with `python3 run_demo.py`.

## Method 4 — Offline bundle

```bash
git bundle create neural-truth-lab.bundle origin/main..HEAD
# transfer bundle to another network/machine, then:
git clone neural-truth-lab.bundle /tmp/repo && cd /tmp/repo
git remote add origin git@github.com:sohamzycus/neural-truth-lab.git
git push origin main
```

## What should be committed

| Commit | Skip (gitignored) |
|--------|-------------------|
| `session6/project/core/` | `project/storage/artifacts/` |
| `session6/project/ledger/` | `project/checkpoints/` |
| `session6/project/models/` | `project/ledgers/` |
| `session6/project/tests/` | `project/submission_artifacts/` |
| `session6/assets/*.mmd, *.png` | `project/forks/` |
| `session6/README.md` | `**/__pycache__/` |

Run `python3 session6/project/run_demo.py` after clone to regenerate evidence locally.
