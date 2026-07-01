#!/usr/bin/env bash
# ponytail: login shell loads mise shims so node/npm are on PATH on Netlify
set -euo pipefail

echo "=== Neural Truth Lab — Netlify build ==="
echo "PWD: $(pwd)"

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "node/npm not on PATH; retrying with login shell"
  exec bash -lc "cd \"$(pwd)\" && bash scripts/netlify-build.sh --inner"
fi

if [[ "${1:-}" == "--inner" ]]; then
  shift
fi

node -v
npm -v

echo "Installing dependencies…"
npm install --include=dev --no-audit --no-fund

if [[ ! -f node_modules/next/package.json ]]; then
  echo "ERROR: next is not installed after npm install"
  ls node_modules 2>/dev/null | head -20 || true
  exit 1
fi

echo "Building…"
npm run build
