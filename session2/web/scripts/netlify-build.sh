#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== SamaBPE Netlify build ==="
node -v
npm -v

npm ci
npm run build

test -f dist/index.html
echo "Build OK"
