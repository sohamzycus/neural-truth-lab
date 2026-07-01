#!/usr/bin/env bash
set -euxo pipefail
cd "$(dirname "$0")/.."

export npm_config_production=false

echo "=== Netlify build ==="
node -v
npm -v

# Netlify's default install often leaves a broken partial node_modules (next missing).
rm -rf node_modules

if ! npm ci --no-audit --no-fund; then
  echo "npm ci failed; falling back to npm install"
  npm install --no-audit --no-fund
fi

if [[ ! -f node_modules/next/package.json ]]; then
  echo "next missing after install; installing explicitly"
  npm install next@15.5.19 --no-audit --no-fund
fi

if [[ ! -f node_modules/next/dist/bin/next ]]; then
  echo "FATAL: next binary still missing"
  ls -la node_modules 2>/dev/null | head -40 || true
  exit 1
fi

# NODE_ENV=development during build breaks static export (Html/404 prerender error).
unset NODE_ENV
npm run build
