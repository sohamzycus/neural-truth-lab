#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-$ROOT/../session11/.venv/bin/python}"
cd "$ROOT"
$PY -m pytest tests/ -q
$PY -m src.experiment --mode baseline --max-steps 5 --tokens 50000 --run-label smoke_baseline
$PY -m src.experiment --mode euler --max-steps 5 --tokens 50000 --run-label smoke_euler
$PY -m src.experiment --mode midpoint --max-steps 5 --tokens 50000 --run-label smoke_midpoint
