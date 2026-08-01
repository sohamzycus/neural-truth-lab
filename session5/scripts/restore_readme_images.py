#!/usr/bin/env python3
"""Replace base64 data URIs in README with GitHub-friendly relative asset paths."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

ALT_TO_FILE = {
    "Capability flow": "capability-flow.png",
    "Reviewer journey": "reviewer-journey.png",
    "DVP pipeline": "dvp-pipeline.png",
    "Capability pie": "capability-pie.png",
    "Indic tiers": "indic-tier-pie.png",
    "Curriculum timeline": "curriculum-timeline.png",
}


def main() -> int:
    text = README.read_text()
    n = text.count("data:image/png;base64,")
    if n == 0:
        print("No embedded images found; already using asset paths")
        return 0

    def repl(m: re.Match) -> str:
        alt, width = m.group(1), m.group(2)
        fname = ALT_TO_FILE.get(alt)
        if not fname:
            raise ValueError(f"Unknown alt: {alt!r}")
        return f'![{alt}](assets/{fname})'

    out = re.sub(
        r'<img src="data:image/png;base64,[^"]+" alt="([^"]+)" width="(\d+)"\s*/>',
        repl,
        text,
    )
    README.write_text(out)
    print(f"Restored {n} images to assets/*.png paths ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
