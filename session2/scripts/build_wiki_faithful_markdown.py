#!/usr/bin/env python3
"""Phase 2 — fetch Wikipedia REST HTML and emit wiki-faithful Markdown snapshots."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import html2text
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import WIKI_CONFIG
from samabpe.evaluator_text import count_wordish_units

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "corpus"
USER_AGENT = "SamaBPE/2.0 (resubmission; wiki-faithful-corpus)"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _html_converter() -> html2text.HTML2Text:
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_tables = False
    h.body_width = 0
    h.unicode_snob = True
    h.single_line_break = False
    return h


def fetch_rest_html(host: str, title: str) -> tuple[str, str | None]:
    """Return (html, revision_id)."""
    encoded = quote(title.replace(" ", "_"), safe="")
    url = f"https://{host}/api/rest_v1/page/html/{encoded}"
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    resp = requests.get(url, headers=headers, timeout=120)
    resp.raise_for_status()
    rev = resp.headers.get("content-revision-id") or resp.headers.get("etag")
    return resp.text, rev


def fetch_revision_id(host: str, title: str) -> str | None:
    api = f"https://{host}/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "revisions",
        "rvprop": "ids",
        "redirects": 1,
    }
    try:
        r = requests.get(api, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        r.raise_for_status()
        pages = r.json()["query"]["pages"]
        page = next(iter(pages.values()))
        revs = page.get("revisions", [])
        if revs:
            return str(revs[0].get("revid"))
    except Exception:
        pass
    return None


def html_to_markdown(html: str) -> str:
    return _html_converter().handle(html).strip() + "\n"


def main() -> int:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    converter = _html_converter()
    ts = datetime.now(timezone.utc).isoformat()

    for lang, cfg in WIKI_CONFIG.items():
        host = cfg["host"]
        title = cfg["title"]
        print(f"Fetching {lang}: {title} @ {host}…")
        html, rev_header = fetch_rest_html(host, title)
        rev_id = fetch_revision_id(host, title) or rev_header
        md = html_to_markdown(html)
        # .txt is the markdown body used for training/evaluation (faithful snapshot).
        txt = md

        md_path = CORPUS_DIR / f"{lang}.faithful.md"
        txt_path = CORPUS_DIR / f"{lang}.faithful.txt"
        meta_path = CORPUS_DIR / f"{lang}.meta.json"

        md_path.write_text(md, encoding="utf-8")
        txt_path.write_text(txt, encoding="utf-8")

        source_url = f"https://{host}/wiki/{quote(title.replace(' ', '_'))}"
        meta = {
            "language": lang,
            "title": title,
            "wikipedia_url": source_url,
            "rest_html_url": f"https://{host}/api/rest_v1/page/html/{quote(title.replace(' ', '_'))}",
            "fetch_timestamp": ts,
            "revision_id": rev_id,
            "character_count": len(md),
            "byte_count": len(md.encode("utf-8")),
            "sha256_md": sha256_text(md),
            "sha256_txt": sha256_text(txt),
            "wordish_unit_count": count_wordish_units(md),
            "format": "wiki-faithful-markdown",
            "converter": "html2text",
        }
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            f"  → {md_path.name} ({meta['character_count']:,} chars, "
            f"{meta['wordish_unit_count']:,} word-ish units)"
        )

    manifest = {
        "generated_at": ts,
        "languages": list(WIKI_CONFIG.keys()),
        "corpus_dir": str(CORPUS_DIR.relative_to(ROOT)),
        "note": "Distinct from data/frozen plain-text corpora — do not replace until analysis complete.",
    }
    (CORPUS_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nCorpus manifest → {CORPUS_DIR / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
