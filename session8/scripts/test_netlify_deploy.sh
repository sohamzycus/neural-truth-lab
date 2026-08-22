#!/usr/bin/env bash
# ponytail: one-off deploy smoke test — prints HTTP codes only, not tokens
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web"

OAUTH=$(node -e "const c=require(process.env.HOME+'/Library/Preferences/netlify/config.json'); const u=Object.values(c.users||{})[0]; process.stdout.write(u?.auth?.token||'')")
PAT=$(curl -fsS -H "Authorization: Bearer $OAUTH" -H "Content-Type: application/json" \
  -d '{"administrator_id":null,"expires_in":2592000,"grant_saml":true,"name":"github-actions-erav5"}' \
  "https://api.netlify.com/api/v1/oauth/applications/create_token" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>process.stdout.write(JSON.parse(d).token.id))")

echo "list_sites: $(curl -s -o /tmp/sites.json -w '%{http_code}' -H "Authorization: Bearer $PAT" https://api.netlify.com/api/v1/sites)"
node -e "const j=require('/tmp/sites.json'); j.forEach(s=>console.log('site',s.name,s.id)); console.log('count',j.length)"
echo "get_site_id: $(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $PAT" https://api.netlify.com/api/v1/sites/15eab089-7b3f-4d94-87bc-14d18bdbbb5f)"
echo "get_site_name: $(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $PAT" https://api.netlify.com/api/v1/sites/attention-evolution-erav5)"

cd dist && zip -qr ../deploy.zip . && cd ..
echo "zip_deploy_id: $(curl -s -o /tmp/nd.json -w '%{http_code}' -H "Authorization: Bearer $PAT" -H "Content-Type: application/zip" --data-binary @deploy.zip https://api.netlify.com/api/v1/sites/15eab089-7b3f-4d94-87bc-14d18bdbbb5f/deploys)"
head -c 120 /tmp/nd.json 2>/dev/null; echo
