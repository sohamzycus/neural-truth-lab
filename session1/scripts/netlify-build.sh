#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Netlify build ==="
node -v

next_bin="node_modules/next/dist/bin/next"

install_deps() {
  if yarn --version 2>/dev/null | grep -q '^1\.'; then
    yarn install --frozen-lockfile --network-timeout 600000
  else
    npx --yes yarn@1.22.22 install --frozen-lockfile --network-timeout 600000
  fi
}

if [[ ! -f "$next_bin" ]]; then
  echo "next missing; installing dependencies..."
  install_deps
fi

if [[ ! -f "$next_bin" ]]; then
  echo "FATAL: next binary still missing after install"
  ls -la node_modules/next 2>/dev/null || ls -la node_modules 2>/dev/null | head -20 || true
  exit 1
fi

# NODE_ENV=development during build breaks static export (Html/404 prerender error).
unset NODE_ENV
node "$next_bin" build
