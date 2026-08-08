"""Content-addressed hashing utilities for the Training Data OS."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(obj: Any) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256_text(canonical)


def verify_hash(obj: Any, expected: str, label: str = "artifact") -> None:
    actual = sha256_json(obj)
    if actual != expected:
        raise ValueError(f"{label} hash mismatch: expected {expected[:16]}… got {actual[:16]}…")
