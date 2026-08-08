"""Append-only event store — Kafka-like immutable event log."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from storage.hash_utils import sha256_json


class EventStore:
    """JSONL append-only event log with monotonic offsets."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        offset = self.count()
        event = {
            "offset": offset,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        event["hash"] = sha256_json({k: v for k, v in event.items() if k != "hash"})
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")
        return event

    def count(self) -> int:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return 0
        with self.path.open(encoding="utf-8") as f:
            return sum(1 for _ in f)

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def read_from(self, offset: int) -> Iterator[dict[str, Any]]:
        for event in self.read_all():
            if event["offset"] >= offset:
                yield event

    def get(self, offset: int) -> dict[str, Any] | None:
        for event in self.read_all():
            if event["offset"] == offset:
                return event
        return None
