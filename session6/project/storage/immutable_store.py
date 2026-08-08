"""Append-only, content-addressed immutable artifact store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from storage.hash_utils import sha256_bytes, sha256_json


class ImmutableStore:
    """Write-once artifact store. Overwrites raise immediately."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for_hash(self, content_hash: str, suffix: str = ".json") -> Path:
        return self.root / content_hash[:2] / f"{content_hash}{suffix}"

    def put_json(self, obj: Any) -> str:
        content_hash = sha256_json(obj)
        path = self._path_for_hash(content_hash)
        if path.exists():
            existing = path.read_bytes()
            if sha256_bytes(existing) != content_hash:
                raise ValueError(f"Hash collision at {path}")
            return content_hash
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True)
        path.write_text(payload, encoding="utf-8")
        return content_hash

    def get_json(self, content_hash: str) -> Any:
        path = self._path_for_hash(content_hash)
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {content_hash}")
        return json.loads(path.read_text(encoding="utf-8"))

    def put_bytes(self, data: bytes, suffix: str = ".bin") -> str:
        content_hash = sha256_bytes(data)
        path = self._path_for_hash(content_hash, suffix=suffix)
        if path.exists():
            return content_hash
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return content_hash

    def put_text(self, text: str, suffix: str = ".txt") -> str:
        return self.put_bytes(text.encode("utf-8"), suffix=suffix)

    def exists(self, content_hash: str) -> bool:
        return self._path_for_hash(content_hash).exists()
