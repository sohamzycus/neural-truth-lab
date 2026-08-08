#!/usr/bin/env bash
# Regenerate session6 diagram PNGs + SVGs from Mermaid sources
set -euo pipefail
cd "$(dirname "$0")/../assets"
for f in architecture differentiators event-sourcing time-machine resilience; do
  echo "Rendering $f..."
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.png" -b white
  npx -y @mermaid-js/mermaid-cli@11 -i "${f}.mmd" -o "${f}.svg" -b white
done
echo "Done. PNG + SVG in session6/assets/"
