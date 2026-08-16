"""Expanded multilingual corpus with reproducible train/val/test splits."""

from __future__ import annotations

import json
import random
from pathlib import Path

# Original benchmark corpus (preserved for backward-compatible metrics)
CORPUS: dict[str, list[str]] = {
    "english": [
        "a", "apple", "hello", "world", "machine", "learning", "embedding",
        "reversible", "kronecker", "dynamic", "representation", "transformer",
        "the quick brown fox", "neural networks", "parameter efficiency",
    ],
    "hindi": [
        "नमस्ते", "भारत", "हिंदी", "भाषा", "कृत्रिम", "बुद्धिमत्ता",
        "मशीन", "सीखना", "एम्बेडिंग", "प्रतिनिधित्व",
    ],
    "telugu": [
        "నమస్కారం", "తెలుగు", "భాష", "యంత్ర", "అభ్యాసం",
        "ఎంబెడ్డింగ్", "ప్రతినిధిత్వం",
    ],
    "bengali": [
        "নমস্কার", "বাংলা", "ভাষা", "মেশিন", "শেখা",
        "এমবেডিং", "প্রতিনিধিত্ব",
    ],
    "numbers": ["0", "9", "42", "99", "12345", "3.14159"],
    "symbols": ["!", "@#$", "→←", "🙂", "🇮🇳", "a·b"],
    "edge": [
        " ", "  ", "a" * 5, "a" * 40, "a" * 100,
        "é", "naïve", "resume", "क" * 20,
        "ab", "ba", "abc", "acb",
    ],
}

EN_WORDS = [
    "alpha", "beta", "gamma", "delta", "model", "token", "vector", "matrix",
    "science", "research", "experiment", "hypothesis", "evidence", "analysis",
    "compression", "decoder", "encoder", "latent", "projection", "capacity",
]
HI_WORDS = ["शब्द", "परीक्षण", "डेटा", "मॉडल", "कोड", "प्रयोग", "परिणाम", "विश्लेषण"]
TE_WORDS = ["పదం", "పరీక్ష", "డేటా", "మోడల్", "కోడ్", "ప్రయోగం", "ఫలితం", "విశ్లేషణ"]
BN_WORDS = ["শব্দ", "পরীক্ষা", "ডেটা", "মডেল", "কোড", "প্রয়োগ", "ফলাফল", "বিশ্লেষণ"]


def _generated_pool(seed: int = 42) -> list[tuple[str, str]]:
    rng = random.Random(seed)
    out: list[tuple[str, str]] = []
    for i in range(120):
        w = rng.choice(EN_WORDS)
        out.append((f"en_{w}_{i}", w if i % 3 else f"{w}_{i}"))
    for i in range(80):
        w = rng.choice(HI_WORDS)
        out.append((f"hi_{i}", f"{w}{i % 10}"))
    for i in range(80):
        w = rng.choice(TE_WORDS)
        out.append((f"te_{i}", f"{w}{i % 10}"))
    for i in range(80):
        w = rng.choice(BN_WORDS)
        out.append((f"bn_{i}", f"{w}{i % 10}"))
    for i in range(40):
        out.append((f"num_{i}", str(rng.randint(0, 999999))))
    for i in range(30):
        sym = rng.choice(["!", "?", "→", "·", "§", "€", "©"])
        out.append((f"sym_{i}", sym * rng.randint(1, 4)))
    for n in [1, 2, 4, 8, 16, 32, 48, 64, 96, 128]:
        out.append((f"rep_a_{n}", "a" * n))
        out.append((f"rep_x_{n}", "x" * n))
    for base in ["ab", "ba", "abc", "acb", "cab", "xyz", "zyx"]:
        for i in range(5):
            out.append((f"perm_{base}_{i}", base + str(i)))
    return out


def build_splits(seed: int = 42) -> dict[str, list[str]]:
    pool = _generated_pool(seed)
    rng = random.Random(seed)
    rng.shuffle(pool)
    n = len(pool)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    train_gen = [s for _, s in pool[:n_train]]
    val_gen = [s for _, s in pool[n_train : n_train + n_val]]
    test_gen = [s for _, s in pool[n_train + n_val :]]
    # Original corpus strings go to train (except explicit held-out originals)
    train = list(dict.fromkeys(all_strings() + train_gen))
    val = list(dict.fromkeys(val_gen))
    test = list(dict.fromkeys(held_out_strings() + test_gen))
    # ensure no overlap train/test
    train_set = set(train)
    test = [s for s in test if s not in train_set]
    val = [s for s in val if s not in train_set]
    return {"train": train, "val": val, "test": test}


_SPLITS: dict[str, list[str]] | None = None


def get_splits(seed: int = 42) -> dict[str, list[str]]:
    global _SPLITS
    if _SPLITS is None:
        _SPLITS = build_splits(seed)
    return _SPLITS


def all_strings() -> list[str]:
    out: list[str] = []
    for items in CORPUS.values():
        out.extend(items)
    return out


def held_out_strings() -> list[str]:
    return [
        "unseen_english_word",
        "अनदेखा",
        "అనదృశ్య",
        "অদেখা",
        "zzzz_new_token",
        "dynamic_kronecker_v2",
    ]


def language_of(s: str) -> str:
    if any("\u0900" <= c <= "\u097f" for c in s):
        return "hindi"
    if any("\u0c00" <= c <= "\u0c7f" for c in s):
        return "telugu"
    if any("\u0980" <= c <= "\u09ff" for c in s):
        return "bengali"
    if s.isascii() or all(ord(c) < 128 for c in s):
        return "english"
    return "other"


def save(path: Path) -> None:
    data = {"corpus": CORPUS, "splits": get_splits()}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
