#!/usr/bin/env bash
# Regenerate session5 diagram PNGs from Mermaid sources
set -euo pipefail
cd "$(dirname "$0")/../assets"
for f in reviewer-journey dvp-pipeline capability-pie indic-tier-pie curriculum-timeline capability-flow; do
  echo "Rendering $f..."
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.png" -b white
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.svg" -b white
done
echo "Done. PNG + SVG in session5/assets/"
python3 "$(dirname "$0")/embed_readme_images.py"
