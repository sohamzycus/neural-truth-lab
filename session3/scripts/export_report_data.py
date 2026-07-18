#!/usr/bin/env python3
"""Copy derived JSON to web/public/data for static viewer."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "derived"
DST = ROOT / "web" / "public" / "data"
MATRICES = ROOT / "data" / "inputs" / "matrices"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for f in SRC.glob("*.json"):
        shutil.copy(f, DST / f.name)
    matrices = {}
    for f in sorted(MATRICES.glob("M*.json")):
        matrices[f.stem] = json.loads(f.read_text())
    (DST / "matrices.json").write_text(json.dumps(matrices, indent=2) + "\n")
    shutil.copy(ROOT / "report" / "REPORT.md", DST.parent / "report.md")
    diag_dst = DST.parent / "diagrams"
    diag_dst.mkdir(exist_ok=True)
    for f in (ROOT / "diagrams" / "src").glob("*.mmd"):
        shutil.copy(f, diag_dst / f.name)
    print(f"exported to {DST} and report.md")


if __name__ == "__main__":
    main()
