#!/usr/bin/env python3
"""Sync frozen resubmission artefacts to submission/ and web/public/."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "results" / "resubmission" / "final"
SUB = ROOT / "submission"
CORPUS = ROOT / "data" / "faithful"
WEB = ROOT / "web" / "public" / "data"


def main() -> int:
    if not (FINAL / "tokenizer.json").exists():
        print("Run scripts/run_weight_search.py first")
        return 1
    SUB.mkdir(parents=True, exist_ok=True)
    (SUB / "corpus").mkdir(exist_ok=True)
    shutil.copy2(FINAL / "tokenizer.json", SUB / "tokenizer.json")
    shutil.copy2(FINAL / "metrics.json", SUB / "metrics.json")
    if (FINAL / "provenance.json").exists():
        shutil.copy2(FINAL / "provenance.json", SUB / "provenance.json")
    for lang in ("en", "hi", "te", "bn"):
        for ext in (".faithful.md", ".faithful.txt", ".meta.json"):
            p = CORPUS / f"{lang}{ext}"
            if p.exists():
                shutil.copy2(p, SUB / "corpus" / p.name)
    shutil.copy2(ROOT / "python" / "samabpe" / "evaluator_contract.py", SUB / "evaluator_contract.py")
    shutil.copy2(ROOT / "scripts" / "build_wiki_faithful_markdown.py", SUB / "build_wiki_faithful_markdown.py")
    subprocess.check_call([sys.executable, str(SUB / "evaluate_tokenizer.py")], cwd=SUB)

    WEB.mkdir(parents=True, exist_ok=True)
    res_dir = WEB / "results"
    sub_dir = WEB / "submission"
    res_dir.mkdir(exist_ok=True)
    sub_dir.mkdir(exist_ok=True)
    metrics = json.loads((FINAL / "metrics.json").read_text(encoding="utf-8"))
    if (FINAL / "provenance.json").exists():
        prov = json.loads((FINAL / "provenance.json").read_text(encoding="utf-8"))
        metrics["provenance"] = {
            "strategy": prov.get("strategy"),
            "weights": prov.get("weights"),
            "experiment_id": prov.get("experiment_id"),
            "constraint_class": prov.get("constraint_class"),
            "english_threshold_pass": prov.get("english_threshold_pass"),
            "hindi_threshold_pass": prov.get("hindi_threshold_pass"),
            "selection_reason": prov.get("selection_reason"),
        }
    comp = ROOT / "results" / "resubmission" / "comparison.json"
    if comp.exists():
        shutil.copy2(comp, res_dir / "resubmission_comparison.json")
    reg = json.loads((ROOT / "results" / "resubmission" / "experiments.json").read_text(encoding="utf-8"))
    (res_dir / "resubmission_experiments.json").write_text(
        json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (res_dir / "resubmission_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    shutil.copy2(FINAL / "tokenizer.json", sub_dir / "tokenizer.json")
    shutil.copy2(SUB / "metrics.json", sub_dir / "metrics.json")
    shutil.copy2(ROOT / "submission" / "encoder.py", sub_dir / "encoder.py")
    shutil.copy2(SUB / "evaluate_tokenizer.py", sub_dir / "evaluate_tokenizer.py")
    if (SUB / "train_tokenizer.py").exists():
        shutil.copy2(SUB / "train_tokenizer.py", sub_dir / "train_tokenizer.py")
    corp_web = sub_dir / "corpus"
    corp_web.mkdir(exist_ok=True)
    for f in (SUB / "corpus").glob("*"):
        shutil.copy2(f, corp_web / f.name)
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "export_playground_parity.py")])
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "generate_verified_submission_data.py")])
    print("Synced resubmission artefacts to submission/ and web/public/data/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
