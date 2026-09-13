"""Configuration hashing — METRIC-* traceability."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
