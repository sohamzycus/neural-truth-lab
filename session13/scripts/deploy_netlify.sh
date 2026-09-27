#!/usr/bin/env bash
# Deploy Session 13 Reversibility Lab (requires NETLIFY_AUTH_TOKEN or netlify login)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web/interactive-lab"
npm run build
SITE_NAME="${NETLIFY_SITE_NAME:-reversibility-lab-erav5}"
if [[ -z "${NETLIFY_AUTH_TOKEN:-}" ]]; then
  echo "Set NETLIFY_AUTH_TOKEN or use: gh workflow run netlify-deploy-session13.yml"
  exit 1
fi
SITE_ID=$(curl -fsS -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
  "https://api.netlify.com/api/v1/sites" | python3 -c "import json,sys; n='$SITE_NAME'; s=json.load(sys.stdin); print(next((x['id'] for x in s if x.get('name')==n), ''))")
if [[ -z "$SITE_ID" ]]; then
  SITE_ID=$(curl -fsS -X POST -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" \
    -H "Content-Type: application/json" -d "{\"name\":\"$SITE_NAME\"}" \
    "https://api.netlify.com/api/v1/sites" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
fi
(cd dist && zip -qr ../deploy.zip .)
curl -fsS -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN" -H "Content-Type: application/zip" \
  --data-binary @deploy.zip "https://api.netlify.com/api/v1/sites/${SITE_ID}/deploys"
echo "https://${SITE_NAME}.netlify.app"
