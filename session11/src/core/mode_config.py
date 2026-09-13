"""Execution mode parameters — SPEC: acceptance_criteria.yaml execution_modes."""

from __future__ import annotations


def bias_steps(mode: str) -> int:
    return 20  # assignment requires 20 steps in all modes


def schedule_total_steps(mode: str) -> int:
    return 300  # assignment requires 300-step training


def schedule_warmup(mode: str) -> int:
    return 30 if mode == "full" else 10


def schedule_stable(mode: str) -> int:
    return 100 if mode == "full" else 30


def ratio_train_steps(mode: str) -> int:
    return 60 if mode == "full" else 40


def ratio_warmup(mode: str) -> int:
    return 10


def ratio_stable(mode: str) -> int:
    return 30 if mode == "full" else 20


def lr_widths(mode: str) -> list[int]:
    return [256, 512, 1024]


def lr_grid_points(mode: str) -> int:
    return 7 if mode == "full" else 5


def lr_train_steps(mode: str) -> int:
    return 100 if mode == "full" else 60
