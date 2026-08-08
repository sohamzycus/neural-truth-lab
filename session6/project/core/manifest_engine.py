"""Manifest engine — aggregates shards into verifiable manifests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from storage.hash_utils import sha256_json
from storage.immutable_store import ImmutableStore


class ManifestEngine:
    """Compiles shard collections into immutable manifests."""

    def __init__(self, store: ImmutableStore) -> None:
        self.store = store
        self.manifests: list[dict[str, Any]] = []

    def create_manifest(
        self,
        *,
        name: str,
        shards: list[dict[str, Any]],
        tokenizer_hash: str,
        curriculum_stage: str,
    ) -> dict[str, Any]:
        shard_refs = [
            {
                "shard_id": s["shard_id"],
                "content_hash": s["content_hash"],
                "lane": s["lane"],
                "evaluation": s["evaluation"],
            }
            for s in shards
        ]
        manifest = {
            "name": name,
            "tokenizer_hash": tokenizer_hash,
            "curriculum_stage": curriculum_stage,
            "shard_count": len(shards),
            "total_tokens": sum(s["num_tokens"] for s in shards),
            "shards": shard_refs,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        manifest["manifest_hash"] = sha256_json(
            {k: v for k, v in manifest.items() if k != "manifest_hash"}
        )
        self.store.put_json(manifest)
        self.manifests.append(manifest)
        return manifest

    def verify_manifest(self, manifest: dict[str, Any]) -> bool:
        expected = sha256_json(
            {k: v for k, v in manifest.items() if k != "manifest_hash"}
        )
        if expected != manifest["manifest_hash"]:
            raise ValueError("Manifest hash verification failed")
        return True
