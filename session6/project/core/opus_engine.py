"""OPUS — always-on quality scoring and admission control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from storage.hash_utils import sha256_json


class OpusDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    DEFERRED = "deferred"
    PROTECTED_OVERRIDE = "protected_override"


@dataclass
class OpusScore:
    quality: float
    novelty: float
    difficulty: float
    composite: float
    decision: OpusDecision
    reason: str


class OpusEngine:
    """Scores every candidate shard; never randomly accepts."""

    def __init__(
        self,
        quality_threshold: float = 0.4,
        novelty_threshold: float = 0.2,
        difficulty_range: tuple[float, float] = (0.1, 0.9),
    ) -> None:
        self.quality_threshold = quality_threshold
        self.novelty_threshold = novelty_threshold
        self.difficulty_range = difficulty_range
        self.decisions: list[dict[str, Any]] = []
        self._seen_hashes: set[str] = set()

    def score_shard(self, shard: dict[str, Any], protected_floor_lane: str | None = None) -> OpusScore:
        content_hash = shard["content_hash"]
        token_count = shard["num_tokens"]

        quality = min(1.0, token_count / 20.0)
        if shard.get("cleaning_version") == "v2":
            quality += 0.1
        quality = min(1.0, quality)

        novelty = 1.0 if content_hash not in self._seen_hashes else 0.1
        self._seen_hashes.add(content_hash)

        # ponytail: difficulty from token-id variance heuristic
        tokens = shard.get("token_ids", [])
        if len(tokens) > 1:
            mean = sum(tokens) / len(tokens)
            variance = sum((t - mean) ** 2 for t in tokens) / len(tokens)
            difficulty = min(1.0, variance / 100.0)
        else:
            difficulty = 0.5

        composite = 0.5 * quality + 0.3 * novelty + 0.2 * difficulty

        if shard.get("evaluation"):
            decision = OpusDecision.DEFERRED
            reason = "evaluation_shard_deferred"
        elif protected_floor_lane and shard["lane"] == protected_floor_lane:
            decision = OpusDecision.PROTECTED_OVERRIDE
            reason = f"protected_floor_override:{protected_floor_lane}"
        elif quality < self.quality_threshold:
            decision = OpusDecision.REJECT
            reason = f"quality_below_threshold:{quality:.3f}"
        elif novelty < self.novelty_threshold and content_hash in self._seen_hashes:
            decision = OpusDecision.REJECT
            reason = "duplicate_content"
        elif difficulty < self.difficulty_range[0]:
            decision = OpusDecision.DEFERRED
            reason = "difficulty_too_low"
        elif difficulty > self.difficulty_range[1]:
            decision = OpusDecision.DEFERRED
            reason = "difficulty_too_high"
        else:
            decision = OpusDecision.ACCEPT
            reason = "passed_all_gates"

        score = OpusScore(
            quality=quality,
            novelty=novelty,
            difficulty=difficulty,
            composite=composite,
            decision=decision,
            reason=reason,
        )
        self._record_decision(shard, score)
        return score

    def _record_decision(self, shard: dict[str, Any], score: OpusScore) -> None:
        record = {
            "shard_id": shard["shard_id"],
            "lane": shard["lane"],
            "quality": score.quality,
            "novelty": score.novelty,
            "difficulty": score.difficulty,
            "composite": score.composite,
            "decision": score.decision.value,
            "reason": score.reason,
            "evaluation": shard.get("evaluation", False),
        }
        record["decision_hash"] = sha256_json(record)
        self.decisions.append(record)

    def filter_accepted(self, shards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        accepted = []
        for shard in shards:
            score = self.score_shard(shard)
            if score.decision in (OpusDecision.ACCEPT, OpusDecision.PROTECTED_OVERRIDE):
                accepted.append(shard)
        return accepted
