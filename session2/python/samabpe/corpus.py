"""Fetch and freeze Wikipedia India articles."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import requests

from samabpe.word_units import count_word_units, normalize_nfc

WIKI_CONFIG = {
    "en": {"host": "en.wikipedia.org", "title": "India"},
    "hi": {"host": "hi.wikipedia.org", "title": "भारत"},
    "te": {"host": "te.wikipedia.org", "title": "భారతదేశం"},
    "bn": {"host": "bn.wikipedia.org", "title": "ভারত"},
}


@dataclass
class CorpusRecord:
    lang: str
    source_url: str
    fetch_timestamp: str
    sha256_raw: str
    sha256_frozen: str
    raw_char_count: int
    normalized_char_count: int
    word_unit_count: int
    title: str


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_article(host: str, title: str) -> tuple[str, str]:
    url = f"https://{host}/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "explaintext": "true",
        "redirects": "1",
    }
    headers = {"User-Agent": "SamaBPE/1.0 (educational; tokenizer-lab)"}
    resp = requests.get(url, params=params, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "missing" in page:
        raise RuntimeError(f"Article not found: {title} on {host}")
    raw = page["extract"]
    source = f"https://{host}/wiki/{requests.utils.quote(title.replace(' ', '_'))}"
    return raw, source


def freeze_text(raw: str) -> str:
    """Documented cleaning: NFC normalize only. Raw preserved separately."""
    return normalize_nfc(raw)


def fetch_all(data_dir: Path | str) -> dict[str, CorpusRecord]:
    data_dir = Path(data_dir)
    raw_dir = data_dir / "raw"
    frozen_dir = data_dir / "frozen"
    raw_dir.mkdir(parents=True, exist_ok=True)
    frozen_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, CorpusRecord] = {}
    ts = datetime.now(timezone.utc).isoformat()

    for lang, cfg in WIKI_CONFIG.items():
        raw, source_url = fetch_article(cfg["host"], cfg["title"])
        frozen = freeze_text(raw)

        raw_path = raw_dir / f"{lang}_india.txt"
        frozen_path = frozen_dir / f"{lang}_india.txt"
        raw_path.write_text(raw, encoding="utf-8")
        frozen_path.write_text(frozen, encoding="utf-8")

        record = CorpusRecord(
            lang=lang,
            source_url=source_url,
            fetch_timestamp=ts,
            sha256_raw=sha256_text(raw),
            sha256_frozen=sha256_text(frozen),
            raw_char_count=len(raw),
            normalized_char_count=len(frozen),
            word_unit_count=count_word_units(frozen),
            title=cfg["title"],
        )
        manifest[lang] = record

    meta_path = data_dir / "corpus_manifest.json"
    meta_path.write_text(
        json.dumps({k: asdict(v) for k, v in manifest.items()}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest


def load_frozen(data_dir: Path | str) -> dict[str, str]:
    frozen_dir = Path(data_dir) / "frozen"
    return {
        lang: (frozen_dir / f"{lang}_india.txt").read_text(encoding="utf-8")
        for lang in WIKI_CONFIG
    }
