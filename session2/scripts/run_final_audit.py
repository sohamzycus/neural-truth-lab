#!/usr/bin/env python3
"""Run full pre/post submission audit and write reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from samabpe.submission_audit import build_audit_report

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final-audit"


def _md_table_fertility(audit: dict) -> str:
    rows = []
    for lang in ("en", "hi", "te", "bn"):
        c = audit["corpora"][lang]
        m = audit["metrics"]
        th = ""
        if lang in ("en", "hi"):
            th = "PASS" if audit["thresholds"][f"{lang}_under_1_2"] else "FAIL"
        rows.append(
            f"| {lang.upper()} | `{c['sha256'][:16]}…` | {m['faithful_unit_counts'][lang]} | "
            f"{m['token_counts'][lang]} | {m['fertilities'][lang]:.6f} | {th or '—'} |"
        )
    return "\n".join(rows)


def _md_vocab(audit: dict) -> str:
    comp = audit["vocabulary_composition"]["categories"]
    total = audit["vocabulary_composition"]["vocab_size"]
    labels = {
        "latin_dominant": "Latin-dominant",
        "devanagari_dominant": "Devanagari-dominant",
        "telugu_dominant": "Telugu-dominant",
        "bengali_dominant": "Bengali-dominant",
        "shared_punctuation_digits_symbols": "Shared punctuation/digits/symbols",
        "mixed_script": "Mixed-script",
        "other_unicode": "Other Unicode",
        "special_token": "Special tokens",
    }
    rows = []
    for k, label in labels.items():
        n = comp[k]
        pct = 100.0 * n / total if total else 0
        rows.append(f"| {label} | {n} | {pct:.1f}% |")
    rows.append(f"| **Total** | **{total}** | **100%** |")
    return "\n".join(rows)


def write_pre_change_audit(audit: dict, path: Path) -> None:
    lines = [
        "# Pre-Change Submission Audit",
        "",
        f"**Verdict:** {audit['verdict']}",
        "",
        "## Authoritative artifacts",
        "",
        "- `submission/tokenizer.json`",
        "- `submission/corpus/{en,hi,te,bn}.faithful.txt` (`.md` identical)",
        f"- Corpus loader: {audit['authoritative_corpus']}",
        "",
        "## Claim classification",
        "",
    ]
    for c in audit["claims"]:
        lines.append(f"- **{c['claim']}**: {c['status']} (saved={c.get('saved')}, fresh={c.get('fresh')})")
    lines.extend(
        [
            "",
            "## Fertility (fresh)",
            "",
            "| Lang | SHA | Faithful units | Tokens | Fertility | Threshold |",
            "| ---- | --- | -------------: | -----: | --------: | --------- |",
            _md_table_fertility(audit),
            "",
            "## Round-trip",
            "",
            f"- Reviewer sample: {'PASS' if audit['roundtrip']['reviewer_sample'] else 'FAIL'}",
        ]
    )
    for lang in ("en", "hi", "te", "bn"):
        ok = audit["roundtrip"]["full_corpus"][lang]
        lines.append(f"- {lang.upper()} full corpus: {'PASS' if ok else 'FAIL'}")
    if audit["discrepancies"]:
        lines.extend(["", "## Discrepancies", ""])
        for d in audit["discrepancies"]:
            lines.append(f"- {d['claim']}: saved {d['saved']} vs fresh {d['fresh']}")
    if audit["hard_stops"]:
        lines.extend(["", "## Hard stops", ""])
        for h in audit["hard_stops"]:
            lines.append(f"- {h}")
    if audit["risks"]:
        lines.extend(["", "## Risks (non-blocking)", ""])
        for r in audit["risks"]:
            lines.append(f"- {r}")
    lines.extend(
        [
            "",
            "## Vocabulary composition",
            "",
            "| Category | Tokens | % |",
            "| -------- | -----: | -: |",
            _md_vocab(audit),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = build_audit_report()
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    write_pre_change_audit(audit, OUT / "pre_change_audit.md")
    print(f"Verdict: {audit['verdict']}")
    print(f"Wrote {OUT / 'audit.json'}")
    return 0 if audit["verdict"] == "SUBMISSION READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
