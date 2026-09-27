#!/usr/bin/env bash
# Full 50M-token assignment runs (GPU recommended for peak-memory metrics).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-$ROOT/../session11/.venv/bin/python}"
cd "$ROOT"
$PY -m pytest tests/ -q
$PY -m src.experiment --mode baseline --tokens 50000000 --run-label baseline_50M
$PY -m src.experiment --mode euler --tokens 50000000 --run-label euler_50M
$PY -m src.experiment --mode midpoint --tokens 50000000 --run-label midpoint_50M
$PY -m src.experiment --mode max_batch --tokens 50000000 --run-label max_batch_50M
$PY scripts/generate_plots.py
cp results/results.json web/interactive-lab/public/data/results.json
