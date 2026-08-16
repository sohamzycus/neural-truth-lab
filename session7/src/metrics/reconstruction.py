"""Reconstruction and collision metrics."""

from __future__ import annotations


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def byte_exact_match(original: bytes, decoded: bytes) -> bool:
    return original == decoded


def string_exact_match(original: str, decoded: str) -> bool:
    return original == decoded


def byte_accuracy(original: bytes, decoded: bytes) -> float:
    if not original and not decoded:
        return 1.0
    max_len = max(len(original), len(decoded))
    matches = sum(1 for i in range(min(len(original), len(decoded))) if original[i] == decoded[i])
    return matches / max_len


def char_accuracy(original: str, decoded: str) -> float:
    if not original and not decoded:
        return 1.0
    max_len = max(len(original), len(decoded))
    matches = sum(1 for i in range(min(len(original), len(decoded))) if original[i] == decoded[i])
    return matches / max_len


def reconstruction_report(original: str, decoded: str) -> dict:
    ob = original.encode("utf-8")
    db = decoded.encode("utf-8", errors="replace")
    return {
        "byte_exact_match": byte_exact_match(ob, db),
        "string_exact_match": string_exact_match(original, decoded),
        "byte_accuracy": round(byte_accuracy(ob, db), 4),
        "char_accuracy": round(char_accuracy(original, decoded), 4),
        "edit_distance": levenshtein(original, decoded),
        "length_preserved": len(original) == len(decoded),
        "original_byte_length": len(ob),
        "decoded_byte_length": len(db),
    }


def find_collisions(strings: list[str], key_fn) -> dict:
    buckets: dict[str, list[str]] = {}
    for s in strings:
        k = key_fn(s)
        buckets.setdefault(k, []).append(s)
    collisions = {k: v for k, v in buckets.items() if len(v) > 1}
    return {
        "total_strings": len(strings),
        "unique_keys": len(buckets),
        "collision_groups": len(collisions),
        "collision_rate": len(collisions) / max(len(strings), 1),
        "examples": list(collisions.items())[:10],
    }
