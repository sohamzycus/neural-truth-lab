#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
python scripts/fetch_corpora.py
python scripts/train.py
python scripts/verify.py
cd web
npm ci
npm test
npm run build
