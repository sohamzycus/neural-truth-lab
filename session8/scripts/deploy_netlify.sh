#!/usr/bin/env bash
# Deploy Session 8 Attention Evolution to Netlify.
# Prerequisite: netlify login (or NETLIFY_AUTH_TOKEN env var)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web"

echo "Building session8/web..."
npm run build

SITE_ID="${NETLIFY_SITE_ID:-15eab089-7b3f-4d94-87bc-14d18bdbbb5f}"
SITE_NAME="${NETLIFY_SITE_NAME:-attention-evolution-erav5}"

if [[ -z "$SITE_ID" ]]; then
  echo "Creating Netlify site: ${SITE_NAME}"
  SITE_ID=$(npx --yes netlify-cli@17 sites:create --name "$SITE_NAME" --account-slug "$(npx --yes netlify-cli@17 api listAccountsForUser | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{const j=JSON.parse(d);console.log(j[0]?.slug||'')})")" 2>/dev/null | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1 || true)
fi

if [[ -z "$SITE_ID" ]]; then
  echo "Set NETLIFY_SITE_ID or run: npx netlify-cli@17 sites:create --name ${SITE_NAME}"
  echo "Then: NETLIFY_SITE_ID=<id> bash scripts/deploy_netlify.sh"
  exit 1
fi

echo "Deploying dist/ to site ${SITE_NAME} (${SITE_ID})"

npx --yes netlify-cli@17 deploy \
  --dir=dist \
  --site="$SITE_ID" \
  --prod \
  --message "ERA V5 Session 8 — Attention Evolution"

echo ""
echo "Live URL: https://${SITE_NAME}.netlify.app"
