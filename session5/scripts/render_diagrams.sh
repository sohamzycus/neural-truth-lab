#!/usr/bin/env bash
# Regenerate session5 diagram PNGs from Mermaid sources
set -euo pipefail
cd "$(dirname "$0")/../assets"
for f in reviewer-journey dvp-pipeline capability-pie indic-tier-pie curriculum-timeline capability-flow opus-pipeline tradeoff-tree capability-evolution risk-tree benchmark-flow; do
  echo "Rendering $f..."
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.png" -b white
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.svg" -b white
done
echo "Done. PNG + SVG in session5/assets/"
echo "README uses assets/*.png paths (GitHub-compatible). For Cursor-only preview: python3 scripts/embed_readme_images.py"
