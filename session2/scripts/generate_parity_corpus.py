"""Generate parity test corpus for Python/browser tokenizer tests."""

from __future__ import annotations

import json
from pathlib import Path

SAMPLES = [
    # English
    "India is a country.",
    "The quick brown fox jumps over the lazy dog.",
    "Tokenization matters for NLP.",
    "Hello world",
    "New\nline\ttab",
    "  repeated   whitespace  ",
    "Price: $42.50",
    "Visit https://example.com/path",
    "Email test@example.org",
    "Numbers 1234567890",
    # Hindi
    "भारत एक देश है।",
    "हिन्दी भाषा",
    "दिल्ली भारत की राजधानी है",
    "कृष्णा",  # combining sequence
    "संयुक्त",  # virama conjunct
    # Telugu
    "భారతదేశం ఒక దేశం.",
    "తెలుగు భాష",
    "హైదరాబాద్",
    "క్ష",  # conjunct fragment
    # Bengali
    "ভারত একটি দেশ।",
    "বাংলা ভাষা",
    "কলকাতা",
    "জ্ঞান",  # conjunct
    # Mixed
    "India भारत భారతదేశం ভারত",
    "India is a diverse country.",
    "भारत एक विविध देश है।",
    "భారతదేశం వైవిధ్యభరితమైన దేశం.",
    "ভারত একটি বৈচিত্র্যময় দেশ।",
    "EN हिन्दी తెలుగు বাংলা mix",
    # Emoji & symbols
    "Flag 🇮🇳 India",
    "Math ∑∫∂",
    "Quote \"test\" and 'apostrophe'",
    # ZWJ/ZWNJ examples (Devanagari)
    "क\u200dष",  # ZWJ
    "क\u200cष",  # ZWNJ
]

for i in range(70):
    SAMPLES.append(f"word{i} भारत word{i} భారత word{i} ভারত")


def generate(out_path: Path) -> list[dict]:
    cases = [{"id": i, "text": s} for i, s in enumerate(SAMPLES[: max(100, len(SAMPLES))])]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    return cases


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    cases = generate(root / "results" / "parity_corpus.json")
    print(f"Wrote {len(cases)} parity cases")
