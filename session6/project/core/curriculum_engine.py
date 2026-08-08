"""Curriculum timeline and mixture schedule compiler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from storage.hash_utils import sha256_json


@dataclass
class LaneWeight:
    lane: str
    weight: float
    protected_floor: float = 0.0


@dataclass
class CurriculumStage:
    name: str
    lanes: list[LaneWeight] = field(default_factory=list)


DEFAULT_CURRICULUM: list[CurriculumStage] = [
    CurriculumStage("stage_a", [
        LaneWeight("english", 40, protected_floor=10),
        LaneWeight("code", 20, protected_floor=5),
        LaneWeight("indic", 40, protected_floor=15),
    ]),
    CurriculumStage("stage_b", [
        LaneWeight("english", 20, protected_floor=5),
        LaneWeight("code", 50, protected_floor=10),
        LaneWeight("indic", 30, protected_floor=10),
    ]),
    CurriculumStage("stage_c", [
        LaneWeight("code", 60, protected_floor=15),
        LaneWeight("agent", 30, protected_floor=10),
        LaneWeight("english", 10, protected_floor=5),
    ]),
]


class CurriculumEngine:
    """Compiles curriculum timeline into actionable mixture schedules."""

    def __init__(self, stages: list[CurriculumStage] | None = None) -> None:
        self.stages = stages or DEFAULT_CURRICULUM
        self.current_stage_idx = 0
        self.compiled_mixtures: list[dict[str, Any]] = []

    @property
    def current_stage(self) -> CurriculumStage:
        return self.stages[self.current_stage_idx]

    def advance_stage(self) -> bool:
        if self.current_stage_idx < len(self.stages) - 1:
            self.current_stage_idx += 1
            return True
        return False

    def compile_mixture(self, available_shards: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
        stage = self.current_stage
        total_weight = sum(lw.weight for lw in stage.lanes)
        planned: dict[str, float] = {}
        for lw in stage.lanes:
            planned[lw.lane] = lw.weight / total_weight

        actual_counts: dict[str, int] = {}
        for lane in planned:
            actual_counts[lane] = len(available_shards.get(lane, []))

        total_shards = sum(actual_counts.values()) or 1
        actual: dict[str, float] = {
            lane: count / total_shards for lane, count in actual_counts.items()
        }

        mixture = {
            "stage": stage.name,
            "planned": planned,
            "actual": actual,
            "protected_floors": {lw.lane: lw.protected_floor for lw in stage.lanes},
            "stage_idx": self.current_stage_idx,
        }
        mixture["mixture_hash"] = sha256_json(
            {k: v for k, v in mixture.items() if k != "mixture_hash"}
        )
        self.compiled_mixtures.append(mixture)
        return mixture

    def select_shards_for_batch(
        self,
        shards_by_lane: dict[str, list[dict[str, Any]]],
        batch_size: int,
        rng_state: list[int],
    ) -> list[dict[str, Any]]:
        """Deterministic shard selection respecting mixture weights and protected floors."""
        stage = self.current_stage
        total_weight = sum(lw.weight for lw in stage.lanes)
        selected: list[dict[str, Any]] = []
        counters: dict[str, int] = {lw.lane: 0 for lw in stage.lanes}

        for i in range(batch_size):
            # ponytail: LCG pseudo-rng for determinism without importing random
            rng_state[0] = (rng_state[0] * 1103515245 + 12345) & 0x7FFFFFFF
            roll = (rng_state[0] % 10000) / 10000.0

            # Check protected floors first
            lane = None
            for lw in stage.lanes:
                floor_count = max(1, int(batch_size * lw.protected_floor / 100))
                if counters[lw.lane] < floor_count and shards_by_lane.get(lw.lane):
                    lane = lw.lane
                    break

            if lane is None:
                cumulative = 0.0
                for lw in stage.lanes:
                    cumulative += lw.weight / total_weight
                    if roll <= cumulative and shards_by_lane.get(lw.lane):
                        lane = lw.lane
                        break
                if lane is None:
                    lane = next(
                        (lw.lane for lw in stage.lanes if shards_by_lane.get(lw.lane)),
                        stage.lanes[0].lane,
                    )

            pool = shards_by_lane.get(lane, [])
            if pool:
                idx = (rng_state[0] + i) % len(pool)
                selected.append(pool[idx])
                counters[lane] = counters.get(lane, 0) + 1

        return selected

    def verify_protected_floors(self, selected: list[dict[str, Any]], batch_size: int) -> bool:
        stage = self.current_stage
        lane_counts: dict[str, int] = {}
        for shard in selected:
            lane_counts[shard["lane"]] = lane_counts.get(shard["lane"], 0) + 1
        for lw in stage.lanes:
            if lw.protected_floor > 0:
                min_count = max(1, int(batch_size * lw.protected_floor / 100))
                if lane_counts.get(lw.lane, 0) < min_count and batch_size >= min_count:
                    return False
        return True
