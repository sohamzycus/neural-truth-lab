#!/usr/bin/env bash
# Deploy Session 7 research webapp to Netlify.
# Prerequisite: netlify login (or NETLIFY_AUTH_TOKEN env var)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

cp results/summary.json app/data/results.json

SITE_ID="${NETLIFY_SITE_ID:-2970b327-1843-45ac-982a-0817ad4484c9}"
SITE_NAME="dynamic-kronecker-session7"

echo "Syncing results → app/data/results.json"
echo "Deploying app/ to site ${SITE_NAME} (${SITE_ID})"

npx --yes netlify-cli@17 deploy \
  --dir=app \
  --site="$SITE_ID" \
  --prod \
  --message "ERA V5 Session 7 — Dynamic Reversible Kronecker"

echo ""
echo "Live URL: https://${SITE_NAME}.netlify.app"
