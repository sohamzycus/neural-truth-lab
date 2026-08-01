#!/usr/bin/env python3
"""Inline session5/assets/*.png into README as base64 data URIs for Cursor preview."""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ASSETS = ROOT / "assets"


def data_uri(name: str) -> str:
    path = ASSETS / name
    if not path.exists():
        raise FileNotFoundError(path)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def embed(content: str) -> str:
    def replace_src(name: str, alt: str = "diagram") -> str:
        return f'<img src="{data_uri(name)}" alt="{alt}" width="800" />'

    # HTML: <img src="assets/foo.png" alt="..." width="..." />
    def html_repl(m: re.Match) -> str:
        file = m.group(1)
        name = file.split("/", 1)[1] if "/" in file else file
        alt = m.group(2) or name
        width = m.group(3) or "800"
        return f'<img src="{data_uri(name)}" alt="{alt}" width="{width}" />'

    content = re.sub(
        r'<img\s+src="assets/([^"]+\.png)"\s+alt="([^"]*)"\s+width="(\d+)"\s*/>',
        html_repl,
        content,
    )

    # markdown: ![alt](assets/foo.png)
    def md_repl(m: re.Match) -> str:
        alt, file = m.group(1), m.group(2).lstrip("./")
        name = file.split("/", 1)[1]
        return replace_src(name, alt)

    content = re.sub(
        r"!\[([^\]]*)\]\((\.?/?assets/[^)]+\.png)\)",
        md_repl,
        content,
    )
    return content


def main() -> int:
    text = README.read_text()
    if "data:image/png;base64," in text:
        print("README already has embedded images; re-embedding from assets")
    out = embed(text)
    README.write_text(out)
    n = out.count("data:image/png;base64,")
    print(f"Embedded {n} images into {README} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
