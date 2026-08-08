#!/usr/bin/env bash
# Push helpers for networks that block GitHub SSH port 22 or HTTPS git push.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BRANCH="${1:-main}"
REMOTE="${2:-origin}"

SSH_CFG="$ROOT/.git/ssh_config_github"
cat > "$SSH_CFG" <<'EOF'
Host github.com
  Hostname ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes
EOF

try_push() {
  local label="$1"
  shift
  echo ""
  echo "=== Trying: $label ==="
  if "$@"; then
    echo "✅ Push succeeded via: $label"
    exit 0
  fi
  echo "❌ Failed: $label"
}

# 1) SSH over port 443 (best when HTTPS returns 403)
try_push "SSH via ssh.github.com:443" \
  env GIT_SSH_COMMAND="ssh -F $SSH_CFG -o StrictHostKeyChecking=accept-new" \
  git push "$REMOTE" "HEAD:$BRANCH"

# 2) HTTPS via GitHub CLI credential helper
try_push "HTTPS via gh auth git-credential" \
  git -c credential.helper='!gh auth git-credential' \
  push "https://github.com/sohamzycus/neural-truth-lab.git" "HEAD:$BRANCH"

# 3) Bundle fallback — upload manually if all network pushes fail
BUNDLE="$ROOT/neural-truth-lab.bundle"
echo ""
echo "=== Creating offline bundle: $BUNDLE ==="
git bundle create "$BUNDLE" "$REMOTE/$BRANCH"..HEAD
cat <<EOF

All online push methods failed.

Offline fallback:
  1. Copy bundle to a machine with GitHub access:
       $BUNDLE
  2. Clone or fetch from bundle:
       git clone $BUNDLE neural-truth-lab-from-bundle
       cd neural-truth-lab-from-bundle
       git remote add origin git@github.com:sohamzycus/neural-truth-lab.git
       git push origin main

Or upload the bundle in GitHub web UI / another network, then:
       git pull <url-to-bundle>
       git push origin main
EOF
exit 1
