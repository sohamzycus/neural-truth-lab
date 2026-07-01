#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Netlify build ==="
node -v
npm -v

next_bin="node_modules/next/dist/bin/next"

# ponytail: incremental install only when needed; never rm -rf node_modules (breaks Netlify cache, npm ci hangs ~8min)
if [[ ! -f "$next_bin" ]]; then
  echo "next missing; running npm install..."
  npm install --no-audit --no-fund --include=dev
fi

if [[ ! -f "$next_bin" ]]; then
  echo "FATAL: next binary still missing after install"
  ls -la node_modules/next 2>/dev/null || ls -la node_modules 2>/dev/null | head -20 || true
  exit 1
fi

# NODE_ENV=development during build breaks static export (Html/404 prerender error).
unset NODE_ENV
node "$next_bin" build
