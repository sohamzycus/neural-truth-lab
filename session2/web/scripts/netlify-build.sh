#!/usr/bin/env bash
# Local/CI helper — Netlify uses netlify.toml command directly.
set -euo pipefail
cd "$(dirname "$0")/.."
npm install --no-audit --no-fund
npm run build
test -f dist/index.html && echo "Build OK"
