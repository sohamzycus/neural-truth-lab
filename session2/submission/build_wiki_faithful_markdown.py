#!/usr/bin/env python3
"""Fetch Wikipedia REST HTML → wiki-faithful Markdown (evaluator corpus)."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.corpus import WIKI_CONFIG
from samabpe.evaluator_contract import count_wordish_units

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "data" / "faithful"
LEGACY_CORPUS = ROOT / "corpus"
USER_AGENT = "SamaBPE/2.0 (resubmission; wiki-faithful-corpus)"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_rest_html(host: str, title: str) -> tuple[str, str | None]:
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
    soup = BeautifulSoup(html, "lxml")
    body = soup.body or soup
    return md_convert(str(body), heading_style="ATX").strip() + "\n"


def main() -> int:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()

    for lang, cfg in WIKI_CONFIG.items():
        host = cfg["host"]
        title = cfg["title"]
        print(f"Fetching {lang}: {title} @ {host}…")
        html, rev_header = fetch_rest_html(host, title)
        rev_id = fetch_revision_id(host, title) or rev_header
        md = html_to_markdown(html)

        md_path = CORPUS_DIR / f"{lang}.faithful.md"
        md_path.write_text(md, encoding="utf-8")

        source_url = f"https://{host}/wiki/{quote(title.replace(' ', '_'))}"
        meta = {
            "language": lang,
            "source_url": source_url,
            "wikipedia_url": source_url,
            "rest_html_url": f"https://{host}/api/rest_v1/page/html/{quote(title.replace(' ', '_'))}",
            "fetch_timestamp": ts,
            "revision_id": rev_id,
            "sha256": sha256_text(md),
            "characters": len(md),
            "bytes": len(md.encode("utf-8")),
            "wordish_units": count_wordish_units(md),
            "format": "wiki-faithful-markdown",
            "pipeline": "rest-html → beautifulsoup → markdownify",
        }
        (CORPUS_DIR / f"{lang}.meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  → {md_path.name} ({meta['characters']:,} chars, {meta['wordish_units']:,} word-ish)")

    manifest = {
        "generated_at": ts,
        "corpus_dir": "data/faithful",
        "note": "Evaluator-compatible corpus; legacy plain text remains in data/frozen/",
    }
    (CORPUS_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # Mirror to legacy corpus/ path for backward compatibility
    LEGACY_CORPUS.mkdir(parents=True, exist_ok=True)
    for lang in WIKI_CONFIG:
        for name in (f"{lang}.faithful.md", f"{lang}.meta.json"):
            src = CORPUS_DIR / name
            if src.exists():
                (LEGACY_CORPUS / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"\nCorpus → {CORPUS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
